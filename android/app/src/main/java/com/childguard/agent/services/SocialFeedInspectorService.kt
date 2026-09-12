package com.childguard.agent.services

import android.accessibilityservice.AccessibilityService
import android.accessibilityservice.GestureDescription
import android.annotation.SuppressLint
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.graphics.Path
import android.graphics.PixelFormat
import android.os.BatteryManager
import android.os.Build
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager
import android.view.Gravity
import android.view.KeyEvent
import android.view.LayoutInflater
import android.view.View
import android.view.WindowManager
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import android.widget.TextView
import com.childguard.agent.R
import com.childguard.agent.network.MqttBridge
import com.google.android.gms.location.LocationServices
import kotlinx.coroutines.*
import org.json.JSONObject
import java.util.Locale

class SocialFeedInspectorService : AccessibilityService() {

    private var overlayView: View? = null
    private var windowManager: WindowManager? = null
    private var isOverlayShowing = false

    private val serviceScope = CoroutineScope(Dispatchers.Default + SupervisorJob())
    private lateinit var mqttBridge: MqttBridge

    // Volume Down SOS Sliding Window Trigger (3 presses in <= 2000ms)
    private val volumePressTimestamps = mutableListOf<Long>()
    private val sosWindowMillis = 2000L
    private val requiredSosTaps = 3

    private val restrictedKeywords = setOf(
        "porn", "nsfw", "18+", "nude", "blood", "beheading", "murder", 
        "weapon", "drugs", "vape", "cigarette", "kill", "casino", "betting"
    )

    override fun onServiceConnected() {
        super.onServiceConnected()
        windowManager = getSystemService(WINDOW_SERVICE) as WindowManager
        mqttBridge = MqttBridge(this)
        serviceScope.launch { mqttBridge.connect() }
        createBlurOverlay()
    }

    override fun onKeyEvent(event: KeyEvent): Boolean {
        if (event.action == KeyEvent.ACTION_DOWN && event.keyCode == KeyEvent.KEYCODE_VOLUME_DOWN) {
            val now = System.currentTimeMillis()
            synchronized(volumePressTimestamps) {
                // Purge taps outside sliding window
                volumePressTimestamps.removeAll { now - it > sosWindowMillis }
                volumePressTimestamps.add(now)

                if (volumePressTimestamps.size >= requiredSosTaps) {
                    volumePressTimestamps.clear()
                    triggerSilentEmergencySos()
                }
            }
        }
        // Let system continue normal volume operation so child remains undetected
        return super.onKeyEvent(event)
    }

    @SuppressLint("MissingPermission")
    private fun triggerSilentEmergencySos() {
        // 1. Subtle stealth haptic pulse confirming transmission
        provideStealthVibration()

        // 2. Query instantaneous battery level
        val batteryStatus: Intent? = IntentFilter(Intent.ACTION_BATTERY_CHANGED).let { filter ->
            registerReceiver(null, filter)
        }
        val level: Int = batteryStatus?.getIntExtra(BatteryManager.EXTRA_LEVEL, -1) ?: -1
        val scale: Int = batteryStatus?.getIntExtra(BatteryManager.EXTRA_SCALE, -1) ?: -1
        val batteryPct: Float = if (level >= 0 && scale > 0) (level * 100 / scale.toFloat()) else -1.0f

        // 3. Obtain high-accuracy last location
        val fusedClient = LocationServices.getFusedLocationProviderClient(this)
        fusedClient.lastLocation.addOnSuccessListener { loc ->
            val lat = loc?.latitude ?: 0.0
            val lon = loc?.longitude ?: 0.0
            val speed = loc?.speed ?: 0.0

            val alert = JSONObject().apply {
                put("type", "EMERGENCY_SOS_ALARM")
                put("severity", "CRITICAL")
                put("trigger", "HARDWARE_TRIPLE_VOLUME_TAP")
                put("snippet", "EMERGENCY: Silent panic signal triggered via physical button triple-tap!")
                put("latitude", lat)
                put("longitude", lon)
                put("speed", speed)
                put("battery_percent", batteryPct)
                put("timestamp", System.currentTimeMillis())
            }

            serviceScope.launch {
                mqttBridge.publishAlert(alert)
            }
        }
    }

    private fun provideStealthVibration() {
        try {
            val vibrator = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                val vm = getSystemService(Context.VIBRATOR_MANAGER_SERVICE) as VibratorManager
                vm.defaultVibrator
            } else {
                @Suppress("DEPRECATION")
                getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
            }

            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                vibrator.vibrate(VibrationEffect.createOneShot(120, VibrationEffect.DEFAULT_AMPLITUDE))
            } else {
                @Suppress("DEPRECATION")
                vibrator.vibrate(120)
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        val rootNode = rootInActiveWindow ?: return

        val visibleText = StringBuilder()
        traverseNodeTree(rootNode, visibleText)

        val fullContent = visibleText.toString().lowercase(Locale.ROOT)

        for (keyword in restrictedKeywords) {
            if (fullContent.contains(keyword)) {
                triggerProtectionIntervention(keyword)
                break
            }
        }
    }

    private fun traverseNodeTree(node: AccessibilityNodeInfo?, builder: StringBuilder) {
        if (node == null) return
        if (node.text != null && node.text.isNotEmpty()) {
            builder.append(node.text).append(" ")
        }
        if (node.contentDescription != null && node.contentDescription.isNotEmpty()) {
            builder.append(node.contentDescription).append(" ")
        }
        for (i in 0 until node.childCount) {
            traverseNodeTree(node.getChild(i), builder)
        }
    }

    private fun triggerProtectionIntervention(triggerReason: String) {
        if (isOverlayShowing) return
        showOverlayBanner("Inappropriate Content Masked: Found $triggerReason")
        executeSkipGesture()
    }

    private fun executeSkipGesture() {
        val metrics = resources.displayMetrics
        val screenHeight = metrics.heightPixels
        val screenWidth = metrics.widthPixels

        // Programmatic swipe-up to skip inappropriate reel or short
        val path = Path().apply {
            moveTo(screenWidth / 2f, screenHeight * 0.8f)
            lineTo(screenWidth / 2f, screenHeight * 0.2f)
        }

        val gesture = GestureDescription.Builder()
            .addStroke(GestureDescription.StrokeDescription(path, 0, 250))
            .build()

        dispatchGesture(gesture, object : GestureResultCallback() {
            override fun onCompleted(gestureDescription: GestureDescription?) {
                overlayView?.postDelayed({ hideOverlay() }, 1000)
            }
        }, null)
    }

    private fun createBlurOverlay() {
        val inflater = LayoutInflater.from(this)
        overlayView = inflater.inflate(R.layout.layout_safety_overlay, null)

        val params = WindowManager.LayoutParams(
            WindowManager.LayoutParams.MATCH_PARENT,
            WindowManager.LayoutParams.MATCH_PARENT,
            WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY,
            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE or WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN,
            PixelFormat.TRANSLUCENT
        ).apply {
            gravity = Gravity.CENTER
        }

        overlayView?.visibility = View.GONE
        windowManager?.addView(overlayView, params)
    }

    private fun showOverlayBanner(message: String) {
        overlayView?.let { view ->
            val txtMsg = view.findViewById<TextView>(R.id.txtWarning)
            txtMsg.text = message
            view.visibility = View.VISIBLE
            isOverlayShowing = true
        }
    }

    private fun hideOverlay() {
        overlayView?.visibility = View.GONE
        isOverlayShowing = false
    }

    override fun onInterrupt() {}

    override fun onDestroy() {
        serviceScope.cancel()
        if (overlayView != null) {
            windowManager?.removeView(overlayView)
        }
        mqttBridge.disconnect()
        super.onDestroy()
    }
}
