package com.childguard.agent.services

import android.service.notification.NotificationListenerService
import android.service.notification.StatusBarNotification
import com.childguard.agent.network.MqttBridge
import kotlinx.coroutines.*
import org.json.JSONObject
import java.util.regex.Pattern

class NotificationMonitorService : NotificationListenerService() {

    private val scope = CoroutineScope(Dispatchers.Default + SupervisorJob())
    private lateinit var mqttBridge: MqttBridge

    // Threat detection rules for harassment, predators, and self-harm keywords
    private val threatPatterns = listOf(
        Pattern.compile("\\b(suicide|kill yourself|hurt you|die|hate you)\\b", Pattern.CASE_INSENSITIVE),
        Pattern.compile("\\b(meet alone|secret place|send photo|nude|don't tell)\\b", Pattern.CASE_INSENSITIVE)
    )

    override fun onCreate() {
        super.onCreate()
        mqttBridge = MqttBridge(this)
        scope.launch { mqttBridge.connect() }
    }

    override fun onNotificationPosted(sbn: StatusBarNotification?) {
        val sbnNotNull = sbn ?: return
        val packageName = sbnNotNull.packageName

        // Monitored apps
        val monitoredApps = setOf(
            "com.whatsapp", 
            "com.instagram.android", 
            "org.telegram.messenger", 
            "com.google.android.apps.messaging"
        )
        if (!monitoredApps.contains(packageName)) return

        val extras = sbnNotNull.notification.extras
        val title = extras.getString("android.title") ?: "Unknown Contact"
        val text = extras.getCharSequence("android.text")?.toString() ?: ""

        if (text.isEmpty()) return

        for (pattern in threatPatterns) {
            if (pattern.matcher(text).find()) {
                dispatchSecurityAlert(packageName, title, text, "CRITICAL_THREAT_KEYWORD")
                break
            }
        }
    }

    private fun dispatchSecurityAlert(pkg: String, sender: String, content: String, reason: String) {
        scope.launch {
            val alert = JSONObject().apply {
                put("type", "CHAT_SECURITY_ALARM")
                put("severity", "HIGH")
                put("app_package", pkg)
                put("sender", sender)
                put("snippet", content.take(100))
                put("trigger", reason)
                put("timestamp", System.currentTimeMillis())
            }
            mqttBridge.publishAlert(alert)
        }
    }

    override fun onDestroy() {
        scope.cancel()
        mqttBridge.disconnect()
        super.onDestroy()
    }
}
