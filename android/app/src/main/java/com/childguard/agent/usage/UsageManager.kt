package com.childguard.agent.usage

import android.app.admin.DevicePolicyManager
import android.app.usage.UsageStatsManager
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import com.childguard.agent.receivers.GuardDeviceAdminReceiver

class UsageManager(private val context: Context) {

    private val usageStatsManager = context.getSystemService(Context.USAGE_STATS_SERVICE) as UsageStatsManager
    private val devicePolicyManager = context.getSystemService(Context.DEVICE_POLICY_SERVICE) as DevicePolicyManager
    private val adminComponent = ComponentName(context, GuardDeviceAdminReceiver::class.java)

    private val restrictedPackages = setOf("com.zhiliaoapp.musically", "com.instagram.android", "com.snapchat.android")

    fun getCurrentForegroundApp(): String? {
        val now = System.currentTimeMillis()
        val stats = usageStatsManager.queryUsageStats(UsageStatsManager.INTERVAL_DAILY, now - 1000 * 60, now)
        return stats?.maxByOrNull { it.lastTimeUsed }?.packageName
    }

    fun isAppRestricted(pkg: String): Boolean {
        return restrictedPackages.contains(pkg)
    }

    fun enforceAppBlock(pkg: String) {
        val homeIntent = Intent(Intent.ACTION_MAIN).apply {
            addCategory(Intent.CATEGORY_HOME)
            flags = Intent.FLAG_ACTIVITY_NEW_TASK
        }
        context.startActivity(homeIntent)
    }

    fun lockDeviceImmediately() {
        if (devicePolicyManager.isAdminActive(adminComponent)) {
            devicePolicyManager.lockNow()
        }
    }
}
