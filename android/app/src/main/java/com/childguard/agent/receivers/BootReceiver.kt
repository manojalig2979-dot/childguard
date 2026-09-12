package com.childguard.agent.receivers

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import com.childguard.agent.services.ChildGuardService

class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val validActions = setOf(
            Intent.ACTION_BOOT_COMPLETED,
            Intent.ACTION_MY_PACKAGE_REPLACED,
            "android.intent.action.QUICKBOOT_POWERON"
        )
        if (intent.action in validActions) {
            ChildGuardService.startService(context)
        }
    }
}
