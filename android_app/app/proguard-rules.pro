# Add project specific ProGuard rules here.
# You can control the set of applied configuration files using the
# signingConfig builds upon the defaults.
# For more details, see
#   http://developer.android.com/guide/developing/tools/proguard.html

# If your project uses WebView with JS, uncomment the following
# and specify the fully qualified class name to the JavaScript interface
# class:
#-keepclassmembers class fqcn.of.javascript.interface.for.webview {
#   public *;
#}

# Uncomment this to preserve the line number information for
# debugging stack traces.
#-keepattributes SourceFile,LineNumberTable

# If you keep the line number information, uncomment this to
# hide the original source file name.
#-renamesourcefileattribute SourceFile

# Keep Retrofit
-keep class retrofit2.** { *; }
-keepattributes Signature
-keepattributes Exceptions

# Keep GSON
-keep class com.google.gson.** { *; }
-keepattributes Signature

# Keep OkHttp
-keep class okhttp3.** { *; }
-keep interface okhttp3.** { *; }
-dontwarn okhttp3.**

# Keep our models
-keep class com.item.assistant.** { *; }
