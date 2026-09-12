import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:mqtt_client/mqtt_client.dart';
import 'package:mqtt_client/mqtt_server_client.dart';

void main() {
  runApp(const ChildGuardParentApp());
}

class ChildGuardParentApp extends StatelessWidget {
  const ChildGuardParentApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'ChildGuard Command Center',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        primaryColor: const Color(0xFF3B82F6),
        scaffoldBackgroundColor: const Color(0xFF0F172A),
        cardColor: const Color(0xFF1E293B),
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFF3B82F6),
          secondary: Color(0xFF10B981),
          error: Color(0xFFEF4444),
          surface: Color(0xFF1E293B),
        ),
      ),
      home: const ParentDashboardScreen(),
    );
  }
}

class ParentDashboardScreen extends StatefulWidget {
  const ParentDashboardScreen({super.key});

  @override
  State<ParentDashboardScreen> createState() => _ParentDashboardScreenState();
}

class _ParentDashboardScreenState extends State<ParentDashboardScreen>
    with SingleTickerProviderStateMixin {
  final String childDeviceId = "child_dev_99182";
  late MqttServerClient client;
  final MapController mapController = MapController();
  late TabController tabController;

  bool isConnected = false;
  String connectionStatus = "Connecting to Broker...";

  // Default initial coordinates centered around school safe zone
  LatLng currentChildLocation = const LatLng(28.6145, 77.2120);
  double currentSpeed = 0.0;
  DateTime lastLocationTime = DateTime.now();

  List<Map<String, dynamic>> threatFeed = [];

  // Spatial Geofence Polygons (Matching PostGIS seed.sql)
  final List<Polygon> geofencePolygons = [
    Polygon(
      points: const [
        LatLng(28.6130, 77.2090),
        LatLng(28.6130, 77.2150),
        LatLng(28.6180, 77.2150),
        LatLng(28.6180, 77.2090),
      ],
      color: const Color(0x3310B981),
      borderColor: const Color(0xFF10B981),
      borderStrokeWidth: 2.0,
      isFilled: true,
      label: 'School Safe Zone',
    ),
    Polygon(
      points: const [
        LatLng(28.6200, 77.2200),
        LatLng(28.6200, 77.2260),
        LatLng(28.6250, 77.2260),
        LatLng(28.6250, 77.2200),
      ],
      color: const Color(0x333B82F6),
      borderColor: const Color(0xFF3B82F6),
      borderStrokeWidth: 2.0,
      isFilled: true,
      label: 'Home Safe Zone',
    ),
    Polygon(
      points: const [
        LatLng(28.6100, 77.2300),
        LatLng(28.6100, 77.2380),
        LatLng(28.6150, 77.2380),
        LatLng(28.6150, 77.2300),
      ],
      color: const Color(0x44EF4444),
      borderColor: const Color(0xFFEF4444),
      borderStrokeWidth: 2.5,
      isFilled: true,
      label: 'Prohibited Danger Zone',
    ),
  ];

  @override
  void initState() {
    super.initState();
    tabController = TabController(length: 3, vsync: this);
    initMqtt();
  }

  Future<void> initMqtt() async {
    client = MqttServerClient.withPort(
        'broker.childguard.internal', 'parent_client_ui', 8883);
    client.secure = true;
    client.keepAlivePeriod = 30;
    client.autoReconnect = true;

    try {
      await client.connect();
      setState(() {
        isConnected = true;
        connectionStatus = "Connected to Child Shield";
      });

      client.subscribe(
          "devices/$childDeviceId/telemetry/location", MqttQos.atMostOnce);
      client.subscribe(
          "devices/$childDeviceId/alerts/safety", MqttQos.atLeastOnce);

      client.updates!.listen((List<MqttReceivedMessage<MqttMessage>> messages) {
        final recMessage = messages[0].payload as MqttPublishMessage;
        final rawJson = const Utf8Decoder().convert(recMessage.payload.message);
        final data = jsonDecode(rawJson);

        if (messages[0].topic.contains("location")) {
          final lat = (data['latitude'] as num).toDouble();
          final lon = (data['longitude'] as num).toDouble();
          final speed = ((data['speed'] ?? 0.0) as num).toDouble();

          setState(() {
            currentChildLocation = LatLng(lat, lon);
            currentSpeed = speed;
            lastLocationTime = DateTime.now();
          });
          mapController.move(currentChildLocation, mapController.camera.zoom);
        } else if (messages[0].topic.contains("alerts")) {
          setState(() {
            threatFeed.insert(0, data);
          });
          _showThreatSnackbar(data);
        }
      });
    } catch (e) {
      setState(() {
        isConnected = false;
        connectionStatus = "Broker Offline: $e";
      });
    }
  }

  void _showThreatSnackbar(Map<String, dynamic> alert) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        backgroundColor: const Color(0xFFDC2626),
        behavior: SnackBarBehavior.floating,
        duration: const Duration(seconds: 5),
        content: Row(
          children: [
            const Icon(Icons.warning_amber_rounded, color: Colors.white),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                "${alert['type']}: ${alert['snippet']}",
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void confirmAndDispatchRemoteLock() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF1E293B),
        title: const Row(
          children: [
            Icon(Icons.lock_reset, color: Colors.redAccent),
            SizedBox(width: 8),
            Text("Emergency Device Lock"),
          ],
        ),
        content: const Text(
          "Are you sure you want to trigger an immediate hardware lock on the child's device? The device screen will shut down and require parent PIN.",
          style: TextStyle(color: Color(0xFFCBD5E1)),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text("Cancel", style: TextStyle(color: Colors.grey)),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFFDC2626)),
            onPressed: () {
              Navigator.pop(ctx);
              _sendLockSignal();
            },
            child: const Text("Lock Device Now"),
          ),
        ],
      ),
    );
  }

  void _sendLockSignal() {
    final builder = MqttClientPayloadBuilder();
    final payload = jsonEncode({
      "action": "LOCK_DEVICE",
      "timestamp": DateTime.now().millisecondsSinceEpoch,
    });
    builder.addString(payload);

    if (isConnected) {
      client.publishMessage(
          "devices/$childDeviceId/commands", MqttQos.atLeastOnce, builder.payload!);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Instant Lock Signal Broadcasted Successfully')),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Error: MQTT connection offline.')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            const Icon(Icons.shield_outlined, color: Color(0xFF3B82F6)),
            const SizedBox(width: 10),
            const Text("ChildGuard", style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(width: 12),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: isConnected ? const Color(0x3310B981) : const Color(0x33EF4444),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: isConnected ? const Color(0xFF10B981) : const Color(0xFFEF4444),
                ),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    width: 8,
                    height: 8,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: isConnected ? const Color(0xFF10B981) : const Color(0xFFEF4444),
                    ),
                  ),
                  const SizedBox(width: 6),
                  Text(
                    isConnected ? "ONLINE" : "OFFLINE",
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                      color: isConnected ? const Color(0xFF10B981) : const Color(0xFFEF4444),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
        backgroundColor: const Color(0xFF0F172A),
        actions: [
          IconButton(
            icon: const Icon(Icons.lock, color: Colors.redAccent),
            tooltip: 'Instant Remote Lock',
            onPressed: confirmAndDispatchRemoteLock,
          ),
        ],
        bottom: TabBar(
          controller: tabController,
          indicatorColor: const Color(0xFF3B82F6),
          tabs: [
            const Tab(icon: Icon(Icons.map_outlined), text: "Live Map"),
            Tab(
              icon: Badge(
                isLabelVisible: threatFeed.isNotEmpty,
                label: Text('${threatFeed.length}'),
                child: const Icon(Icons.security_outlined),
              ),
              text: "Threats",
            ),
            const Tab(icon: Icon(Icons.insights_outlined), text: "AI Report"),
          ],
        ),
      ),
      body: TabBarView(
        controller: tabController,
        children: [
          _buildLiveMapTab(),
          _buildThreatFeedTab(),
          _buildAiReportTab(),
        ],
      ),
    );
  }

  Widget _buildLiveMapTab() {
    return Stack(
      children: [
        FlutterMap(
          mapController: mapController,
          options: MapOptions(
            initialCenter: currentChildLocation,
            initialZoom: 15.0,
            minZoom: 10.0,
            maxZoom: 18.0,
          ),
          children: [
            TileLayer(
              urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
              userAgentPackageName: 'com.childguard.parent',
            ),
            PolygonLayer(polygons: geofencePolygons),
            MarkerLayer(
              markers: [
                Marker(
                  point: currentChildLocation,
                  width: 60,
                  height: 60,
                  child: Column(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(4),
                        decoration: BoxDecoration(
                          color: const Color(0xFF3B82F6),
                          shape: BoxShape.circle,
                          boxShadow: [
                            BoxShadow(
                              color: const Color(0xFF3B82F6).withOpacity(0.5),
                              blurRadius: 10,
                              spreadRadius: 3,
                            ),
                          ],
                        ),
                        child: const Icon(
                          Icons.person_pin_circle,
                          color: Colors.white,
                          size: 28,
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
                        decoration: BoxDecoration(
                          color: Colors.black87,
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: const Text(
                          "Aarav",
                          style: TextStyle(fontSize: 9, color: Colors.white),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ],
        ),
        Positioned(
          top: 16,
          left: 16,
          right: 16,
          child: Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xEE1E293B),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: const Color(0xFF334155)),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      "Target: $childDeviceId",
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      "Lat: ${currentChildLocation.latitude.toStringAsFixed(4)}, Lon: ${currentChildLocation.longitude.toStringAsFixed(4)}",
                      style: const TextStyle(fontSize: 11, color: Color(0xFF94A3B8)),
                    ),
                  ],
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text(
                      "Speed: ${currentSpeed.toStringAsFixed(1)} m/s",
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF10B981),
                        fontSize: 13,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      "${lastLocationTime.hour.toString().padLeft(2, '0')}:${lastLocationTime.minute.toString().padLeft(2, '0')}:${lastLocationTime.second.toString().padLeft(2, '0')}",
                      style: const TextStyle(fontSize: 10, color: Color(0xFF94A3B8)),
                    ),
                  ],
                ),
                IconButton(
                  icon: const Icon(Icons.my_location, color: Color(0xFF3B82F6)),
                  tooltip: 'Re-center Map',
                  onPressed: () => mapController.move(currentChildLocation, 15.0),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildThreatFeedTab() {
    if (threatFeed.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.verified_user_outlined, size: 64, color: Colors.green.shade400),
            const SizedBox(height: 16),
            const Text(
              "All Systems Green",
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            const Text(
              "No safety violations, predator threats, or geofence breaches detected.",
              style: TextStyle(color: Color(0xFF94A3B8)),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(12),
      itemCount: threatFeed.length,
      itemBuilder: (ctx, idx) {
        final item = threatFeed[idx];
        final severity = item['severity'] ?? "HIGH";
        final isCritical = severity == "CRITICAL";

        return Card(
          margin: const EdgeInsets.symmetric(vertical: 6),
          color: isCritical ? const Color(0xFF3B1212) : const Color(0xFF1E293B),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(10),
            side: BorderSide(
              color: isCritical ? const Color(0xFFEF4444) : const Color(0xFF334155),
              width: 1,
            ),
          ),
          child: ListTile(
            leading: Icon(
              Icons.warning_rounded,
              color: isCritical ? const Color(0xFFEF4444) : Colors.orangeAccent,
              size: 32,
            ),
            title: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  item['type'] ?? "SECURITY_ALERT",
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: isCritical ? Colors.red : Colors.orange,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    severity,
                    style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold),
                  ),
                ),
              ],
            ),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: 4),
                Text(
                  item['snippet'] ?? item['trigger'] ?? "Violation intercepted.",
                  style: const TextStyle(color: Color(0xFFE2E8F0), fontSize: 12),
                ),
                const SizedBox(height: 4),
                Text(
                  "Rule: ${item['trigger'] ?? 'Keyword match'}",
                  style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 10),
                ),
              ],
            ),
            trailing: Text(
              DateTime.fromMillisecondsSinceEpoch(item['timestamp'] ?? 0)
                  .toLocal()
                  .toString()
                  .split('.')[0]
                  .split(' ')[1],
              style: const TextStyle(fontSize: 10, color: Colors.grey),
            ),
          ),
        );
      },
    );
  }

  Widget _buildAiReportTab() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Overall Safety Score Gauge Card
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0xFF1E293B), Color(0xFF0F172A)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: const Color(0xFF334155)),
          ),
          child: Row(
            children: [
              Stack(
                alignment: Alignment.center,
                children: [
                  SizedBox(
                    width: 80,
                    height: 80,
                    child: CircularProgressIndicator(
                      value: 0.94,
                      strokeWidth: 8,
                      backgroundColor: const Color(0xFF334155),
                      valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFF10B981)),
                    ),
                  ),
                  const Text(
                    "94",
                    style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.white),
                  ),
                ],
              ),
              const SizedBox(width: 20),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: const Color(0x3310B981),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: const Color(0xFF10B981)),
                      ),
                      child: const Text(
                        "Optimal Protection",
                        style: TextStyle(color: Color(0xFF10B981), fontSize: 11, fontWeight: FontWeight.bold),
                      ),
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      "Weekly Child Safety Index",
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 4),
                    const Text(
                      "Aarav's behavioral and spatial metrics demonstrate exemplary digital safety.",
                      style: TextStyle(fontSize: 12, color: Color(0xFF94A3B8)),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),

        // Key Metrics Grid
        Row(
          children: [
            Expanded(
              child: _buildMetricCard(
                icon: Icons.pin_drop,
                iconColor: const Color(0xFF10B981),
                title: "Safe-Zone Rate",
                value: "96.4%",
                subtitle: "School & Home",
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildMetricCard(
                icon: Icons.timer,
                iconColor: const Color(0xFF3B82F6),
                title: "Screen Time",
                value: "18.5 hrs",
                subtitle: "Avg 2.6h / day",
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: _buildMetricCard(
                icon: Icons.shield,
                iconColor: const Color(0xFF8B5CF6),
                title: "Threats Neutralized",
                value: "6 Events",
                subtitle: "Chat & Social skips",
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildMetricCard(
                icon: Icons.dangerous,
                iconColor: const Color(0xFFEF4444),
                title: "Danger Breaches",
                value: "0 Breaches",
                subtitle: "100% Safe Corridor",
              ),
            ),
          ],
        ),
        const SizedBox(height: 20),

        // Screen Time Category Breakdown Card
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: const Color(0xFF1E293B),
            borderRadius: BorderRadius.circular(14),
            border: Border.all(color: const Color(0xFF334155)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                "Weekly App Time Balance",
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
              ),
              const SizedBox(height: 12),
              ClipRRect(
                borderRadius: BorderRadius.circular(6),
                child: SizedBox(
                  height: 12,
                  child: Row(
                    children: [
                      Expanded(flex: 42, child: Container(color: const Color(0xFF10B981))),
                      Expanded(flex: 26, child: Container(color: const Color(0xFF3B82F6))),
                      Expanded(flex: 20, child: Container(color: const Color(0xFF8B5CF6))),
                      Expanded(flex: 12, child: Container(color: const Color(0xFFF59E0B))),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 12),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  _buildLegendItem("Education", "42%", const Color(0xFF10B981)),
                  _buildLegendItem("Family Chat", "26%", const Color(0xFF3B82F6)),
                  _buildLegendItem("Videos", "20%", const Color(0xFF8B5CF6)),
                  _buildLegendItem("Games", "12%", const Color(0xFFF59E0B)),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 20),

        // AI Parental Guidance Recommendations
        const Text(
          "AI Parental Guidance & Insights",
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
        ),
        const SizedBox(height: 8),
        _buildGuidanceCard(
          icon: Icons.check_circle_outline,
          iconColor: const Color(0xFF10B981),
          title: "Consistent Spatial Routine",
          body: "Aarav stayed inside Delhi Public School and Home boundaries consistently throughout the school week.",
        ),
        _buildGuidanceCard(
          icon: Icons.lightbulb_outline,
          iconColor: const Color(0xFFF59E0B),
          title: "Evening Digital Curfew Suggestion",
          body: "Video streaming app usage peaked after 8:45 PM. Setting a 9:00 PM automated app bedtime will enhance sleep quality.",
        ),
        _buildGuidanceCard(
          icon: Icons.health_and_safety_outlined,
          iconColor: const Color(0xFF3B82F6),
          title: "Proactive Defense In Action",
          body: "On-device social feed guardian intercepted 4 restricted video captions and auto-skipped them without minor exposure.",
        ),
      ],
    );
  }

  Widget _buildMetricCard({
    required IconData icon,
    required Color iconColor,
    required String title,
    required String value,
    required String subtitle,
  }) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: const Color(0xFF1E293B),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFF334155)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: iconColor, size: 24),
          const SizedBox(height: 8),
          Text(title, style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 11)),
          const SizedBox(height: 2),
          Text(value, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
          const SizedBox(height: 2),
          Text(subtitle, style: const TextStyle(color: Color(0xFF64748B), fontSize: 10)),
        ],
      ),
    );
  }

  Widget _buildLegendItem(String label, String pct, Color color) {
    return Row(
      children: [
        Container(width: 8, height: 8, decoration: BoxDecoration(color: color, shape: BoxShape.circle)),
        const SizedBox(width: 4),
        Text("$label $pct", style: const TextStyle(fontSize: 10, color: Color(0xFF94A3B8))),
      ],
    );
  }

  Widget _buildGuidanceCard({
    required IconData icon,
    required Color iconColor,
    required String title,
    required String body,
  }) {
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 6),
      color: const Color(0xFF1E293B),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: const BorderSide(color: Color(0xFF334155)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, color: iconColor, size: 24),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                  const SizedBox(height: 4),
                  Text(body, style: const TextStyle(fontSize: 12, color: Color(0xFFCBD5E1))),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
