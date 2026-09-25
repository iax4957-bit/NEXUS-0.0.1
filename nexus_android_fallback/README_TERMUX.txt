NEXUS 0.0.1 - Android Java Fallback package

This package restores the saved Java NEXUS engine files and adds a tested runtime fallback:
PRIMARY: parallel execution
FALLBACK: dependency-aware sequential execution

IMPORTANT:
Do not delete the existing android_app_v1 folder.
The commands below create a backup of the current Java source first.

TERMUX:
1) cd ~/NEXUS-0.0.1/android_app_v1
2) mkdir -p backup_before_fallback
3) cp -r src/com/nexus backup_before_fallback/
4) cd ~/NEXUS-0.0.1
5) unzip -o ~/storage/downloads/NEXUS_android_fallback.zip

The ZIP is arranged so that its src/ directory merges into android_app_v1/src/.
If unzip reports an existing-file prompt, use the -o command exactly as above.

The standalone fallback test source is in:
test/NexusFallbackTest.java

The engine files are under:
src/com/nexus/test/nexus/
