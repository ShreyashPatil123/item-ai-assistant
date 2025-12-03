package com.item.assistant

import com.google.gson.Gson
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import java.util.concurrent.TimeUnit

data class CommandRequest(
    val command: String,
    val source: String = "android"
)

data class CommandResponse(
    val success: Boolean,
    val message: String,
    val result: String? = null
)

data class HealthResponse(
    val status: String
)

class ApiClient(
    private val laptopIp: String,
    private val port: Int,
    private val authToken: String
) {
    private val client = OkHttpClient.Builder()
        .connectTimeout(10, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build()

    private val gson = Gson()
    private val baseUrl = "http://$laptopIp:$port"

    suspend fun sendCommand(command: String): CommandResponse {
        val request = CommandRequest(command = command)
        val json = gson.toJson(request)

        val httpRequest = Request.Builder()
            .url("$baseUrl/api/command")
            .addHeader("Authorization", "Bearer $authToken")
            .addHeader("Content-Type", "application/json")
            .post(json.toRequestBody("application/json".toMediaType()))
            .build()

        return client.newCall(httpRequest).execute().use { response ->
            if (response.isSuccessful) {
                val body = response.body?.string() ?: "{}"
                gson.fromJson(body, CommandResponse::class.java)
            } else {
                CommandResponse(
                    success = false,
                    message = "HTTP ${response.code}: ${response.message}"
                )
            }
        }
    }

    suspend fun checkHealth(): HealthResponse {
        val httpRequest = Request.Builder()
            .url("$baseUrl/health")
            .get()
            .build()

        return client.newCall(httpRequest).execute().use { response ->
            if (response.isSuccessful) {
                val body = response.body?.string() ?: "{}"
                gson.fromJson(body, HealthResponse::class.java)
            } else {
                HealthResponse(status = "offline")
            }
        }
    }
}
