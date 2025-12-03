package com.item.assistant

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch

class SettingsActivity : AppCompatActivity() {

    private lateinit var authTokenInput: EditText
    private lateinit var laptopIpInput: EditText
    private lateinit var portInput: EditText
    private lateinit var testButton: Button
    private lateinit var saveButton: Button
    private lateinit var statusMessage: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_settings)

        // Initialize views
        authTokenInput = findViewById(R.id.authTokenInput)
        laptopIpInput = findViewById(R.id.laptopIpInput)
        portInput = findViewById(R.id.portInput)
        testButton = findViewById(R.id.testButton)
        saveButton = findViewById(R.id.saveButton)
        statusMessage = findViewById(R.id.statusMessage)

        // Load saved settings
        loadSettings()

        // Set up button listeners
        testButton.setOnClickListener { testConnection() }
        saveButton.setOnClickListener { saveSettings() }
    }

    private fun loadSettings() {
        val prefs = getSharedPreferences("ItemSettings", MODE_PRIVATE)
        authTokenInput.setText(prefs.getString("auth_token", "") ?: "")
        laptopIpInput.setText(prefs.getString("laptop_ip", "192.168.1.100") ?: "192.168.1.100")
        portInput.setText(prefs.getInt("api_port", 8765).toString())
    }

    private fun testConnection() {
        val token = authTokenInput.text.toString().trim()
        val ip = laptopIpInput.text.toString().trim()
        val port = portInput.text.toString().toIntOrNull() ?: 8765

        if (token.isEmpty() || ip.isEmpty()) {
            statusMessage.text = "❌ Please fill in all fields"
            statusMessage.setTextColor(android.graphics.Color.RED)
            return
        }

        lifecycleScope.launch {
            try {
                val apiClient = ApiClient(ip, port, token)
                val health = apiClient.checkHealth()

                if (health.status == "healthy") {
                    statusMessage.text = "✅ Connection successful!"
                    statusMessage.setTextColor(android.graphics.Color.GREEN)
                } else {
                    statusMessage.text = "❌ Connection failed"
                    statusMessage.setTextColor(android.graphics.Color.RED)
                }
            } catch (e: Exception) {
                statusMessage.text = "❌ Error: ${e.message}"
                statusMessage.setTextColor(android.graphics.Color.RED)
            }
        }
    }

    private fun saveSettings() {
        val token = authTokenInput.text.toString().trim()
        val ip = laptopIpInput.text.toString().trim()
        val port = portInput.text.toString().toIntOrNull() ?: 8765

        if (token.isEmpty() || ip.isEmpty()) {
            Toast.makeText(this, "Please fill in all fields", Toast.LENGTH_SHORT).show()
            return
        }

        val prefs = getSharedPreferences("ItemSettings", MODE_PRIVATE)
        prefs.edit().apply {
            putString("auth_token", token)
            putString("laptop_ip", ip)
            putInt("api_port", port)
            apply()
        }

        statusMessage.text = "✅ Settings saved!"
        statusMessage.setTextColor(android.graphics.Color.GREEN)
        Toast.makeText(this, "Settings saved successfully", Toast.LENGTH_SHORT).show()
    }
}
