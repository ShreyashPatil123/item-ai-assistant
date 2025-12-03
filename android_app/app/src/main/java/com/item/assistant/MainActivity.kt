package com.item.assistant

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch

class MainActivity : AppCompatActivity() {

    private lateinit var responseText: TextView
    private lateinit var commandInput: EditText
    private lateinit var sendButton: Button
    private lateinit var voiceButton: Button
    private lateinit var historyButton: Button
    private lateinit var settingsButton: Button
    private lateinit var statusText: TextView

    private lateinit var apiClient: ApiClient

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Initialize views
        responseText = findViewById(R.id.responseText)
        commandInput = findViewById(R.id.commandInput)
        sendButton = findViewById(R.id.sendButton)
        voiceButton = findViewById(R.id.voiceButton)
        historyButton = findViewById(R.id.historyButton)
        settingsButton = findViewById(R.id.settingsButton)
        statusText = findViewById(R.id.statusText)

        // Initialize API client
        val prefs = getSharedPreferences("ItemSettings", MODE_PRIVATE)
        val ip = prefs.getString("laptop_ip", "192.168.1.100") ?: "192.168.1.100"
        val port = prefs.getInt("api_port", 8765)
        val token = prefs.getString("auth_token", "") ?: ""

        apiClient = ApiClient(ip, port, token)

        // Set up button listeners
        sendButton.setOnClickListener { sendCommand() }
        settingsButton.setOnClickListener { openSettings() }
        voiceButton.setOnClickListener { startVoiceInput() }
        historyButton.setOnClickListener { showHistory() }

        // Check connection status
        checkConnectionStatus()
    }

    private fun sendCommand() {
        val command = commandInput.text.toString().trim()
        if (command.isEmpty()) {
            responseText.text = "Please enter a command"
            return
        }

        lifecycleScope.launch {
            try {
                val response = apiClient.sendCommand(command)
                if (response.success) {
                    responseText.text = "✅ ${response.message}\n\nResult: ${response.result}"
                    commandInput.text.clear()
                } else {
                    responseText.text = "❌ ${response.message}"
                }
            } catch (e: Exception) {
                responseText.text = "❌ Error: ${e.message}"
            }
        }
    }

    private fun checkConnectionStatus() {
        lifecycleScope.launch {
            try {
                val health = apiClient.checkHealth()
                if (health.status == "healthy") {
                    statusText.text = "🟢 Online"
                    statusText.setTextColor(android.graphics.Color.GREEN)
                } else {
                    statusText.text = "🔴 Offline"
                    statusText.setTextColor(android.graphics.Color.RED)
                }
            } catch (e: Exception) {
                statusText.text = "🔴 Offline"
                statusText.setTextColor(android.graphics.Color.RED)
            }
        }
    }

    private fun openSettings() {
        startActivity(Intent(this, SettingsActivity::class.java))
    }

    private fun startVoiceInput() {
        responseText.text = "Voice input not yet implemented"
    }

    private fun showHistory() {
        responseText.text = "Command history not yet implemented"
    }
}
