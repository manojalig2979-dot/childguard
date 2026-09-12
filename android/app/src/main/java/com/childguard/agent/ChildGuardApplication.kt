package com.childguard.agent

import android.app.Application
import net.sqlcipher.database.SQLiteDatabase

class ChildGuardApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        // Initialize SQLCipher encrypted database engine
        SQLiteDatabase.loadLibs(this)
    }
}
