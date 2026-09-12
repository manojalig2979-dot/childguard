package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"
	"time"

	mqtt "github.com/eclipse/paho.mqtt.golang"
	_ "github.com/lib/pq"
)

type LocationPayload struct {
	Latitude  float64 `json:"latitude"`
	Longitude float64 `json:"longitude"`
	Speed     float64 `json:"speed"`
	Timestamp int64   `json:"timestamp"`
}

type SafetyAlertPayload struct {
	Type       string `json:"type"`
	Severity   string `json:"severity"`
	AppPackage string `json:"app_package,omitempty"`
	Sender     string `json:"sender,omitempty"`
	Snippet    string `json:"snippet"`
	Trigger    string `json:"trigger"`
	Timestamp  int64  `json:"timestamp"`
}

type GeofenceCheckResult struct {
	ID         string
	ZoneName   string
	IsSafeZone bool
	IsInside   bool
}

var (
	db         *sql.DB
	mqttClient mqtt.Client
)

func main() {
	var err error
	connStr := "postgres://postgres:secure_db_pass@localhost:5432/childguard?sslmode=disable"
	db, err = sql.Open("postgres", connStr)
	if err != nil {
		log.Fatalf("Database connection failure: %v", err)
	}
	defer db.Close()

	mqttOpts := mqtt.NewClientOptions().
		AddBroker("ssl://broker.childguard.internal:8883").
		SetClientID("cloud_ingestor_worker_01").
		SetCleanSession(false).
		SetAutoReconnect(true)

	mqttClient = mqtt.NewClient(mqttOpts)
	if token := mqttClient.Connect(); token.Wait() && token.Error() != nil {
		log.Printf("Warning: MQTT Connection failed (%v). Retrying in background...", token.Error())
	}

	mqttClient.Subscribe("devices/+/telemetry/location", 0, func(c mqtt.Client, m mqtt.Message) {
		go processLocationMessage(m.Topic(), m.Payload())
	})

	mqttClient.Subscribe("devices/+/alerts/safety", 1, func(c mqtt.Client, m mqtt.Message) {
		go processAlertMessage(m.Topic(), m.Payload())
	})

	// Start DPDP 30-day compliance retention worker
	stopRetentionWorker := make(chan struct{})
	go startDataRetentionPruner(stopRetentionWorker)

	log.Println("ChildGuard Ingestion Pipeline & Geofence Intelligence Engine Running.")
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)
	<-sigChan

	close(stopRetentionWorker)
	if mqttClient.IsConnected() {
		mqttClient.Disconnect(250)
	}
}

func processLocationMessage(topic string, data []byte) {
	var payload LocationPayload
	if err := json.Unmarshal(data, &payload); err != nil {
		log.Printf("Invalid location JSON received: %v", err)
		return
	}

	var deviceUid string
	fmt.Sscanf(topic, "devices/%s/telemetry/location", &deviceUid)
	if deviceUid == "" {
		return
	}

	// 1. Resolve child record
	var childId string
	err := db.QueryRow("SELECT id FROM children WHERE device_uid = $1", deviceUid).Scan(&childId)
	if err != nil {
		// If child device is not yet registered in database, store by device UID directly if schema allows or log
		log.Printf("Device UID %s not registered in children table: %v", deviceUid, err)
		return
	}

	// 2. Insert into location history with PostGIS point geometry
	query := `
		INSERT INTO location_history (child_id, location, speed, recorded_at)
		VALUES ($1, ST_SetSRID(ST_MakePoint($2, $3), 4326), $4, $5);
	`
	t := time.UnixMilli(payload.Timestamp)
	if payload.Timestamp == 0 {
		t = time.Now()
	}

	_, err = db.Exec(query, childId, payload.Longitude, payload.Latitude, payload.Speed, t)
	if err != nil {
		log.Printf("Failed to record location for child %s: %v", childId, err)
	}

	// 3. Evaluate geofence boundaries against current coordinates
	evaluateGeofences(childId, deviceUid, payload.Longitude, payload.Latitude)
}

func evaluateGeofences(childId string, deviceUid string, lon, lat float64) {
	query := `
		SELECT id, zone_name, is_safe_zone,
		       ST_Contains(boundary, ST_SetSRID(ST_MakePoint($1, $2), 4326)) AS is_inside
		FROM geofences
		WHERE child_id = $3;
	`

	rows, err := db.Query(query, lon, lat, childId)
	if err != nil {
		log.Printf("Geofence spatial evaluation error: %v", err)
		return
	}
	defer rows.Close()

	hasSafeZones := false
	insideAnySafeZone := false

	for rows.Next() {
		var res GeofenceCheckResult
		if err := rows.Scan(&res.ID, &res.ZoneName, &res.IsSafeZone, &res.IsInside); err != nil {
			continue
		}

		if res.IsSafeZone {
			hasSafeZones = true
			if res.IsInside {
				insideAnySafeZone = true
			}
		} else {
			// Danger zone evaluation: Child must NEVER be inside
			if res.IsInside {
				triggerGeofenceAlert(childId, deviceUid, "DANGER_ZONE_BREACH", "CRITICAL",
					fmt.Sprintf("Child entered restricted danger zone: %s", res.ZoneName),
					"ST_Contains(DangerZone, Location) == TRUE")
			}
		}
	}

	// Safe zone perimeter evaluation:
	if hasSafeZones && !insideAnySafeZone {
		triggerGeofenceAlert(childId, deviceUid, "SAFE_ZONE_EXIT", "HIGH",
			"Child is outside all designated safe zones (school, home, activity centers)",
			"OutsideAllSafeZones == TRUE")
	}
}

func triggerGeofenceAlert(childId, deviceUid, alertType, severity, snippet, trigger string) {
	nowMillis := time.Now().UnixMilli()
	alert := SafetyAlertPayload{
		Type:      alertType,
		Severity:  severity,
		Snippet:   snippet,
		Trigger:   trigger,
		Timestamp: nowMillis,
	}

	payloadBytes, err := json.Marshal(alert)
	if err != nil {
		return
	}

	// Store alert in DB
	query := `
		INSERT INTO security_alerts (child_id, alert_type, severity, payload)
		VALUES ($1, $2, $3, $4);
	`
	_, err = db.Exec(query, childId, alertType, severity, string(payloadBytes))
	if err != nil {
		log.Printf("Failed to persist geofence alert: %v", err)
	}

	// Broadcast alert to parent dashboard over MQTT
	if mqttClient != nil && mqttClient.IsConnected() {
		topic := fmt.Sprintf("devices/%s/alerts/safety", deviceUid)
		token := mqttClient.Publish(topic, 1, false, payloadBytes)
		token.Wait()
		log.Printf("[GEOFENCE ALARM] Dispatched %s to topic %s", alertType, topic)
	}
}

func processAlertMessage(topic string, data []byte) {
	var alert SafetyAlertPayload
	if err := json.Unmarshal(data, &alert); err != nil {
		return
	}

	var deviceUid string
	fmt.Sscanf(topic, "devices/%s/alerts/safety", &deviceUid)

	query := `
		INSERT INTO security_alerts (child_id, alert_type, severity, payload)
		SELECT id, $1, $2, $3 FROM children WHERE device_uid = $4;
	`
	_, err := db.Exec(query, alert.Type, alert.Severity, string(data), deviceUid)
	if err != nil {
		log.Printf("Failed to store safety alert: %v", err)
	}
}

// startDataRetentionPruner enforces India DPDP Act 2023 30-day retention purge
func startDataRetentionPruner(stopChan chan struct{}) {
	ticker := time.NewTicker(1 * time.Hour)
	defer ticker.Stop()

	log.Println("[DPDP Retention Worker] Initialized 30-day geolocation auto-pruner.")

	for {
		select {
		case <-stopChan:
			log.Println("[DPDP Retention Worker] Shutting down.")
			return
		case <-ticker.C:
			purgeQuery := `
				DELETE FROM location_history
				WHERE recorded_at < NOW() - INTERVAL '30 days';
			`
			res, err := db.Exec(purgeQuery)
			if err != nil {
				log.Printf("[DPDP Retention Worker] Error executing purge: %v", err)
			} else {
				rowsAffected, _ := res.RowsAffected()
				if rowsAffected > 0 {
					log.Printf("[DPDP Retention Worker] Purged %d expired location breadcrumbs (> 30 days old).", rowsAffected)
				}
			}
		}
	}
}
