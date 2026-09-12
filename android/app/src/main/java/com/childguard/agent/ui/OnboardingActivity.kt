package com.childguard.agent.ui

import android.Manifest
import android.app.AppOpsManager
import android.app.admin.DevicePolicyManager
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Color
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.PowerManager
import android.os.Process
import android.provider.Settings
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.app.NotificationManagerCompat
import androidx.core.content.ContextCompat
import com.childguard.agent.R
import com.childguard.agent.receivers.GuardDeviceAdminReceiver
import com.childguard.agent.services.ChildGuardService
import com.childguard.agent.services.SocialFeedInspectorService
import com.google.android.material.card.MaterialCardView

class OnboardingActivity : AppCompatActivity() {

    private lateinit var txtProgress: TextView
    private lateinit var btnActivateShield: Button

    private lateinit var cardDeviceAdmin: MaterialCardView
    private lateinit var btnDeviceAdmin: Button

    private lateinit var cardAccessibility: MaterialCardView
    private lateinit var btnAccessibility: Button

    private lateinit var cardNotification: MaterialCardView
    private lateinit var btnNotification: Button

    private lateinit var cardUsage: MaterialCardView
    private lateinit var btnUsage: Button

    private lateinit var cardOverlay: MaterialCardView
    private lateinit var btnOverlay: Button

    private lateinit var cardLocation: MaterialCardView
    private lateinit var btnLocation: Button

    private lateinit var cardBattery: MaterialCardView
    private lateinit var btnBattery: Button

    companion object {
        private const val REQUEST_LOCATION_CODE = 2001
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_onboarding)

        bindViews()
        setupListeners()
    }

    override fun onResume() {
        super.onResume()
        refreshPermissionStates()
    }

    private fun bindViews() {
        txtProgress = findViewById(R.id.txtProgress)
        btnActivateShield = findViewById(R.id.btnActivateShield)

        cardDeviceAdmin = findViewById(R.id.cardDeviceAdmin)
        btnDeviceAdmin = findViewById(R.id.btnDeviceAdmin)

        cardAccessibility = findViewById(R.id.cardAccessibility)
        btnAccessibility = findViewById(R.id.btnAccessibility)

        cardNotification = findViewById(R.id.cardNotification)
        btnNotification = findViewById(R.id.btnNotification)

        cardUsage = findViewById(R.id.cardUsage)
        btnUsage = findViewById(R.id.btnUsage)

        cardOverlay = findViewById(R.id.cardOverlay)
        btnOverlay = findViewById(R.id.btnOverlay)

        cardLocation = findViewById(R.id.cardLocation)
        btnLocation = findViewById(R.id.btnLocation)

        cardBattery = findViewById(R.id.cardBattery)
        btnBattery = findViewById(R.id.btnBattery)
    }

    private fun setupListeners() {
        val adminComponent = ComponentName(this, GuardDeviceAdminReceiver::class.java)

        btnDeviceAdmin.setOnClickListener {
            val intent = Intent(DevicePolicyManager.ACTION_ADD_DEVICE_ADMIN).apply {
                putExtra(DevicePolicyManager.EXTRA_DEVICE_ADMIN, adminComponent)
                putExtra(DevicePolicyManager.EXTRA_ADD_EXPLANATION, "ChildGuard requires Device Admin to prevent unauthorized uninstallation.")
            }
            startActivity(intent)
        }

        btnAccessibility.setOnClickListener {
            startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS))
        }

        btnNotification.setOnClickListener {
            startActivity(Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS))
        }

        btnUsage.setOnClickListener {
            startActivity(Intent(Settings.ACTION_USAGE_ACCESS_SETTINGS))
        }

        btnOverlay.setOnClickListener {
            val intent = Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION, Uri.parse("package:$packageName"))
            startActivity(intent)
        }

        btnLocation.setOnClickListener {
            val permissions = mutableListOf(
                Manifest.permission.ACCESS_FINE_LOCATION,
                Manifest.permission.ACCESS_COARSE_LOCATION
            )
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                permissions.add(Manifest.permission.ACCESS_BACKGROUND_LOCATION)
            }
            ActivityCompat.requestPermissions(this, permissions.toTypedArray(), REQUEST_LOCATION_CODE)
        }

        btnBattery.setOnClickListener {
            val intent = Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS, Uri.parse("package:$packageName"))
            startActivity(intent)
        }

        btnActivateShield.setOnClickListener {
            ChildGuardService.startService(this)
            Toast.makeText(this, "ChildGuard Protection Shield is now ACTIVE!", Toast.LENGTH_LONG).show()
            finish()
        }
    }

    private fun refreshPermissionStates() {
        var grantedCount = 0

        // 1. Device Admin
        val dpm = getSystemService(Context.DEVICE_POLICY_SERVICE) as DevicePolicyManager
        val adminComponent = ComponentName(this, GuardDeviceAdminReceiver::class.java)
        val isAdmin = dpm.isAdminActive(adminComponent)
        updateStatus(cardDeviceAdmin, btnDeviceAdmin, isAdmin)
        if (isAdmin) grantedCount++

        // 2. Accessibility
        val expectedComponent = ComponentName(this, SocialFeedInspectorService::class.java).flattenToString()
        val enabledServices = Settings.Secure.getString(contentResolver, Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES) ?: ""
        val isA11y = enabledServices.contains(expectedComponent)
        updateStatus(cardAccessibility, btnAccessibility, isA11y)
        if (isA11y) grantedCount++

        // 3. Notification Listener
        val isNotif = NotificationManagerCompat.getEnabledListenerPackages(this).contains(packageName)
        updateStatus(cardNotification, btnNotification, isNotif)
        if (isNotif) grantedCount++

        // 4. Usage Stats
        val appOps = getSystemService(Context.APP_OPS_SERVICE) as AppOpsManager
        val mode = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            appOps.unsafeCheckOpNoThrow(AppOpsManager.OPSTR_GET_USAGE_STATS, Process.myUid(), packageName)
        } else {
            @Suppress("DEPRECATION")
            appOps.checkOpNoThrow(AppOpsManager.OPSTR_GET_USAGE_STATS, Process.myUid(), packageName)
        }
        val isUsage = (mode == AppOpsManager.MODE_ALLOWED)
        updateStatus(cardUsage, btnUsage, isUsage)
        if (isUsage) grantedCount++

        // 5. System Overlay
        val isOverlay = Settings.canDrawOverlays(this)
        updateStatus(cardOverlay, btnOverlay, isOverlay)
        if (isOverlay) grantedCount++

        // 6. Location
        val fineLocation = ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED
        val bgLocation = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_BACKGROUND_LOCATION) == PackageManager.PERMISSION_GRANTED
        } else true
        val isLocation = fineLocation && bgLocation
        updateStatus(cardLocation, btnLocation, isLocation)
        if (isLocation) grantedCount++

        // 7. Battery Optimization
        val pm = getSystemService(Context.POWER_SERVICE) as PowerManager
        val isBattery = pm.isIgnoringBatteryOptimizations(packageName)
        updateStatus(cardBattery, btnBattery, isBattery)
        if (isBattery) grantedCount++

        txtProgress.text = "Authorization Status: $grantedCount / 7 Granted"

        // Enable master activation once minimum critical guardian privileges are active
        btnActivateShield.isEnabled = (grantedCount >= 5)
        if (btnActivateShield.isEnabled) {
            btnActivateShield.setBackgroundColor(Color.parseColor("#10B981"))
        } else {
            btnActivateShield.setBackgroundColor(Color.parseColor("#334155"))
        }
    }

    private fun updateStatus(card: MaterialCardView, button: Button, isGranted: Boolean) {
        if (isGranted) {
            button.text = "Active"
            button.isEnabled = false
            button.setBackgroundColor(Color.parseColor("#059669"))
            card.strokeColor = Color.parseColor("#10B981")
        } else {
            button.text = "Enable"
            button.isEnabled = true
            button.setBackgroundColor(Color.parseColor("#3B82F6"))
            card.strokeColor = Color.parseColor("#334155")
        }
    }
}
