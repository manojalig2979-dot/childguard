package com.childguard.agent.services

import android.app.*
import android.content.Context
import android.content.Intent
import android.graphics.Color
import android.os.Build
import android.os.IBinder
import androidx.core.app.NotificationCompat
import com.childguard.agent.R
import com.childguard.agent.location.LocationTracker
import com.childguard.agent.network.MqttBridge
import com.childguard.agent.usage.UsageManager
import kotlinx.coroutines.*

class ChildGuardService : Service() {

    private val serviceJob = SupervisorJob()
    private val serviceScope = CoroutineScope(Dispatchers.Default + serviceJob)
    
    private lateinit var locationTracker: LocationTracker
    private lateinit var mqttBridge: MqttBridge
    private lateinit var usageManager: UsageManager

    companion object {
        private const val NOTIFICATION_CHANNEL_ID = "childguard_daemon_channel"
        private const val NOTIFICATION_ID = 1001
        
        fun startService(context: Context) {
            val intent = Intent(context, ChildGuardService::class.java)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                context.startForegroundService(intent)
            } else {
                context.startService(intent)
            }
        }
    }

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
        startForeground(NOTIFICATION_ID, buildForegroundNotification())

        locationTracker = LocationTracker(this)
        mqttBridge = MqttBridge(this)
        usageManager = UsageManager(this)

        initializeSubsystems()
    }

    private fun initializeSubsystems() {
        serviceScope.launch {
            mqttBridge.connect()

            // Start adaptive location tracking
            locationTracker.startTracking { locationData ->
                serviceScope.launch {
                    mqttBridge.publishLocation(locationData)
                }
            }

            // Periodic App Usage Poller (Runs every 60 seconds)
            while (isActive) {
                val currentForegroundApp = usageManager.getCurrentForegroundApp()
                if (currentForegroundApp != null) {
                    val isRestricted = usageManager.isAppRestricted(currentForegroundApp)
                    if (isRestricted) {
                        usageManager.enforceAppBlock(currentForegroundApp)
                    }
                }
                delay(60_000L)
            }
        }
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                NOTIFICATION_CHANNEL_ID,
                "ChildGuard Security Shield",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Monitors device security parameters actively."
                lightColor = Color.BLUE
                lockscreenVisibility = Notification.VISIBILITY_SECRET
            }
            val manager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            manager.createNotificationChannel(channel)
        }
    }

    private fun buildForegroundNotification(): Notification {
        return NotificationCompat.Builder(this, NOTIFICATION_CHANNEL_ID)
            .setContentTitle("ChildGuard Shield Active")
            .setContentText("Parental device protection is safeguarding this device.")
            .setSmallIcon(R.drawable.ic_shield)
            .setOngoing(true)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Sticky restart if killed by OS under low memory pressure
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        serviceJob.cancel()
        locationTracker.stopTracking()
        mqttBridge.disconnect()
        super.onDestroy()
    }
}
