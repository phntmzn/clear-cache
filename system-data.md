**92 GB of System Data on macOS is a lot, but it doesn't necessarily mean macOS itself is taking up 92 GB.** System Data is a catch-all category that includes files macOS doesn't classify elsewhere. Some of it can be safely removed, but other files are needed by your applications or the operating system.

## 1. What is using your 92 GB?

Common causes include:

| Category | Possible size | What it contains |
|---|---:|---|
| Time Machine local snapshots | 5–50+ GB | Local backups stored on your internal drive |
| Xcode and developer files | 5–40+ GB | Build artifacts, DerivedData, simulators, device support |
| Application caches | 2–20+ GB | Cached files from apps such as browsers and development tools |
| iPhone/iPad backups | 5–50+ GB | Local device backups |
| Docker data | 5–50+ GB | Container images, volumes, and build caches |
| Python environments | 1–20+ GB | Virtual environments, downloaded packages, model dependencies |
| AI/LLM model files | 2–100+ GB | Downloaded models, weights, and datasets |
| Logs and temporary files | 1–10+ GB | Diagnostic reports, logs, and temporary application data |

These are illustrative ranges, not estimates of what's actually on your Mac. The exact breakdown depends on your installed software and usage.

Since you're working with Python and PyTorch projects, it's worth checking your development files and any downloaded AI models.

## 2. Find out what's taking up the space

Instead of deleting files immediately, let's investigate first.

### Step 1: Check your disk usage

Open Terminal in macOS and run:

```bash
df -h /
```

This shows your total disk capacity, used space, and available space.

### Step 2: Find the largest folders in your home directory

Run:

```bash
du -h -d 1 ~/Library 2>/dev/null | sort -hr | head -20
```

This lists the 20 largest directories directly inside your user Library folder.

Next, check your caches:

```bash
du -h -d 1 ~/Library/Caches 2>/dev/null | sort -hr | head -20
```

And your application support files:

```bash
du -h -d 1 ~/Library/Application\ Support 2>/dev/null | sort -hr | head -20
```

**These commands only inspect your files; they don't delete anything.**

### Step 3: Check for Time Machine snapshots

Local snapshots can occupy substantial space.

Run:

```bash
tmutil listlocalsnapshots /
```

If snapshots are listed, macOS may be retaining local backups.

To see additional APFS disk-usage information, run:

```bash
diskutil apfs list
```

Don't delete snapshots blindly. macOS can automatically remove eligible local snapshots when it needs space.

### Step 4: Check for Xcode and developer files

If you have Xcode or Apple's developer tools installed, run:

```bash
du -sh ~/Library/Developer/Xcode/DerivedData 2>/dev/null
du -sh ~/Library/Developer/Xcode/Archives 2>/dev/null
du -sh ~/Library/Developer/CoreSimulator 2>/dev/null
```

These directories can grow significantly during development.

Xcode's `DerivedData` generally contains regenerable build artifacts. However, archives may contain valuable app builds, and simulator directories may contain data you want to preserve.

### Step 5: Check for Python and AI files

Inspect your common model and development directories:

```bash
du -sh ~/Documents 2>/dev/null
du -sh ~/Downloads 2>/dev/null
du -sh ~/.cache 2>/dev/null
du -sh ~/.ollama 2>/dev/null
```

The last two commands check your home-directory cache and, if present, your Ollama model storage.

You can also check whether Docker is using space:

```bash
docker system df
```

This command requires Docker to be installed.

---

## 3. Safely reclaim some space

Once you've identified the source, you can choose the appropriate cleanup.

### Clear user application caches

Your Python cache-cleaning script can help, but deleting everything under `~/Library/Caches` isn't guaranteed to reclaim much space.

You can inspect the largest cache directories first:

```bash
du -h -d 1 ~/Library/Caches 2>/dev/null | sort -hr | head -20
```

Then close the relevant applications and remove only caches you understand.

### Clear Python's download cache

If you use pip, inspect its cache size:

```bash
python3 -m pip cache info
```

If you want to remove cached package downloads:

```bash
python3 -m pip cache purge
```

This removes pip's cache, not your installed packages or virtual environments. Packages may need to be downloaded again later.

### Remove unused Docker data

First inspect the usage:

```bash
docker system df
```

If you understand what is unused, this command removes unused Docker resources:

```bash
docker system prune
```

Review the confirmation prompt carefully. Don't add `--volumes` unless you've verified that no important data is stored in unused volumes.

### Restart your Mac

A restart can release temporary storage and allow macOS to recalculate storage usage. It won't necessarily remove persistent files or substantially reduce System Data.

---

## 4. Check what macOS reports

Open:

**Apple menu → System Settings → General → Storage**

Wait for the storage categories to finish calculating.

The System Data category can include files that are difficult for macOS to classify, so its reported size doesn't necessarily correspond to one folder.

Avoid manually deleting files from `/System`, `/private/var`, or other protected system directories to reduce this number.

---

## Let's identify your actual 92 GB

Rather than deleting random files, **run these three commands** in Terminal and share their output:

```bash
du -h -d 1 ~/Library 2>/dev/null | sort -hr | head -15
```

```bash
du -sh ~/.cache ~/Library/Caches ~/Library/Developer ~/.ollama 2>/dev/null
```

```bash
tmutil listlocalsnapshots /
```

I'll help you interpret the results and identify which files are the best candidates for cleanup.
