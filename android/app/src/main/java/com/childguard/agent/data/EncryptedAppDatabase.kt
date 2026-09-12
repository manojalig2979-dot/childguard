package com.childguard.agent.data

import androidx.room.*
import android.content.Context
import net.sqlcipher.database.SupportFactory

@Entity(tableName = "telemetry_queue")
data class TelemetryRecord(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    @ColumnInfo(name = "topic") val topic: String,
    @ColumnInfo(name = "payload") val payload: String,
    @ColumnInfo(name = "created_at") val createdAt: Long = System.currentTimeMillis()
)

@Dao
interface TelemetryDao {
    @Insert
    suspend fun insertRecord(record: TelemetryRecord)

    @Query("SELECT * FROM telemetry_queue ORDER BY created_at ASC LIMIT 50")
    suspend fun getPendingBatch(): List<TelemetryRecord>

    @Delete
    suspend fun deleteBatch(records: List<TelemetryRecord>)
}

@Database(entities = [TelemetryRecord::class], version = 1, exportSchema = false)
abstract class EncryptedAppDatabase : RoomDatabase() {
    abstract fun telemetryDao(): TelemetryDao

    companion object {
        @Volatile private var INSTANCE: EncryptedAppDatabase? = null

        fun getInstance(context: Context, passphrase: ByteArray): EncryptedAppDatabase {
            return INSTANCE ?: synchronized(this) {
                val factory = SupportFactory(passphrase)
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    EncryptedAppDatabase::class.java,
                    "childguard_encrypted.db"
                ).openHelperFactory(factory).build()
                INSTANCE = instance
                instance
            }
        }
    }
}
