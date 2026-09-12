package com.childguard.agent.network

import android.content.Context
import org.eclipse.paho.client.mqttv3.*
import org.json.JSONObject

class MqttBridge(private val context: Context) {

    private val brokerUri = "ssl://broker.childguard.internal:8883"
    private val deviceId = "child_dev_99182"
    private var client: MqttAsyncClient? = null

    fun connect() {
        try {
            client = MqttAsyncClient(brokerUri, deviceId, null)
            val options = MqttConnectOptions().apply {
                isCleanSession = false
                isAutomaticReconnect = true
                keepAliveInterval = 60
                userName = deviceId
                password = "client_signed_jwt_token".toCharArray()
            }

            client?.setCallback(object : MqttCallbackExtended {
                override fun connectComplete(reconnect: Boolean, serverURI: String?) {
                    subscribeToParentCommands()
                }
                override fun connectionLost(cause: Throwable?) {}
                override fun messageArrived(topic: String?, message: MqttMessage?) {
                    handleIncomingCommand(topic, message)
                }
                override fun deliveryComplete(token: IMqttDeliveryToken?) {}
            })

            client?.connect(options)
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    private fun subscribeToParentCommands() {
        client?.subscribe("devices/$deviceId/commands", 1)
    }

    private fun handleIncomingCommand(topic: String?, message: MqttMessage?) {
        val payload = String(message?.payload ?: return)
        val json = JSONObject(payload)
        val action = json.optString("action")
        
        if (action == "LOCK_DEVICE") {
            val usageManager = com.childguard.agent.usage.UsageManager(context)
            usageManager.lockDeviceImmediately()
        }
    }

    fun publishLocation(data: JSONObject) {
        if (client?.isConnected == true) {
            val message = MqttMessage(data.toString().toByteArray()).apply { qos = 0 }
            client?.publish("devices/$deviceId/telemetry/location", message)
        }
    }

    fun publishAlert(alert: JSONObject) {
        if (client?.isConnected == true) {
            val message = MqttMessage(alert.toString().toByteArray()).apply { qos = 1 }
            client?.publish("devices/$deviceId/alerts/safety", message)
        }
    }

    fun disconnect() {
        try {
            client?.disconnect()
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
}
