import os
import sys
import time
import queue
import threading
import traceback
import subprocess
from pathlib import Path

import pyttsx3
import speech_recognition as sr


class VoiceResponder:
	def __init__(self, preferred_gender: str = "female", rate_delta: int = -10, volume: float = 1.0):
		self._engine = pyttsx3.init()
		self._select_voice(preferred_gender)
		# Adjust speaking rate and volume
		rate = self._engine.getProperty("rate")
		self._engine.setProperty("rate", max(120, rate + rate_delta))
		self._engine.setProperty("volume", max(0.0, min(volume, 1.0)))

	def _select_voice(self, preferred_gender: str) -> None:
		voices = self._engine.getProperty("voices")
		selected = None
		preferred_gender_lower = (preferred_gender or "").strip().lower()
		for v in voices:
			# On Windows (SAPI5), female voices typically include 'Female' or 'Zira' in name
			name = (getattr(v, "name", "") or "").lower()
			desc = (getattr(v, "description", "") or "").lower()
			if preferred_gender_lower in ("female", "woman", "girl"):
				if "female" in name or "female" in desc or "zira" in name:
					selected = v
					break
		if selected is None and voices:
			selected = voices[0]
		if selected is not None:
			self._engine.setProperty("voice", selected.id)

	def say(self, text: str) -> None:
		self._engine.say(text)
		self._engine.runAndWait()


class SpeechListener:
	def __init__(self, energy_threshold: int = 300, pause_threshold: float = 0.6):
		self._recognizer = sr.Recognizer()
		self._recognizer.energy_threshold = energy_threshold
		self._recognizer.pause_threshold = pause_threshold
		self._mic = sr.Microphone()

	def calibrate(self, seconds: float = 1.0) -> None:
		with self._mic as source:
			self._recognizer.adjust_for_ambient_noise(source, duration=seconds)

	def listen_once(self, timeout: float | None = None, phrase_time_limit: float | None = 10.0) -> str | None:
		with self._mic as source:
			audio = self._recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
		try:
			# Uses Google Web Speech API (no key needed for short requests)
			return self._recognizer.recognize_google(audio)
		except sr.UnknownValueError:
			return None
		except sr.RequestError:
			return None


class FileAgent:
	def __init__(self, base_dir: str | None = None):
		self.base_dir = Path(base_dir) if base_dir else Path.home()

	def _resolve_path(self, path_str: str) -> Path:
		clean = path_str.strip().strip('"').strip("'")
		p = Path(clean)
		if not p.is_absolute():
			p = self.base_dir / p
		return p.expanduser().resolve()

	def list_folder(self, folder: str) -> list[str]:
		p = self._resolve_path(folder)
		if not p.exists() or not p.is_dir():
			raise FileNotFoundError(f"Folder not found: {p}")
		return [item.name for item in p.iterdir()]

	def read_file(self, file_path: str, max_chars: int = 1200) -> str:
		p = self._resolve_path(file_path)
		if not p.exists() or not p.is_file():
			raise FileNotFoundError(f"File not found: {p}")
		text = p.read_text(errors="ignore")
		if len(text) > max_chars:
			return text[:max_chars] + "..."
		return text

	def open_file(self, file_path: str) -> None:
		p = self._resolve_path(file_path)
		if not p.exists():
			raise FileNotFoundError(f"Path not found: {p}")
		if sys.platform.startswith("win"):
			os.startfile(str(p))
		else:
			opener = "open" if sys.platform == "darwin" else "xdg-open"
			subprocess.Popen([opener, str(p)])

	def search_files(self, name_part: str, within: str | None = None, max_results: int = 25) -> list[str]:
		root = self._resolve_path(within) if within else self.base_dir
		name_lower = name_part.lower()
		results: list[str] = []
		for dirpath, _, filenames in os.walk(root):
			for fname in filenames:
				if name_lower in fname.lower():
					results.append(str(Path(dirpath) / fname))
					if len(results) >= max_results:
						return results
		return results


def parse_command(text: str) -> dict:
	if not text:
		return {"intent": "none"}
	q = text.strip().lower()
	# Exit intents
	if any(k in q for k in ["exit", "quit", "stop agent", "stop listening", "goodbye"]):
		return {"intent": "exit"}
	# List folder
	if q.startswith("list folder") or q.startswith("list files") or q.startswith("show folder"):
		folder = q.replace("list folder", "").replace("list files", "").replace("show folder", "").strip()
		return {"intent": "list_folder", "folder": folder or "."}
	# Search files
	if q.startswith("search file") or q.startswith("find file") or q.startswith("search for"):
		phrase = q.replace("search file", "").replace("find file", "").replace("search for", "").strip()
		return {"intent": "search_files", "name": phrase}
	# Read file
	if q.startswith("read file") or q.startswith("read the file"):
		file_path = q.replace("read file", "").replace("read the file", "").strip()
		return {"intent": "read_file", "path": file_path}
	# Open file
	if q.startswith("open file") or q.startswith("open"):
		file_path = q.replace("open file", "").replace("open", "").strip()
		return {"intent": "open_file", "path": file_path}
	# Time
	if "what time" in q or q.startswith("time"):
		return {"intent": "time"}
	# Help
	if "help" in q:
		return {"intent": "help"}
	# Fallback small talk
	return {"intent": "chat", "text": text}


HELP_TEXT = (
	"You can say: list folder Downloads; search file report; read file Documents/notes.txt; "
	"open file Pictures/photo.jpg; what time is it; exit."
)


def main() -> None:
	responder = VoiceResponder(preferred_gender="female")
	listener = SpeechListener()
	files = FileAgent(base_dir=str(Path.home()))

	print("Calibrating microphone... Please be quiet.")
	listener.calibrate(1.0)
	print("Ready. Speak a command. Say 'help' for options. Say 'exit' to quit.")
	responder.say("Hello! I'm ready. Say a command, or say help for options.")

	while True:
		print("Listening...")
		text = listener.listen_once(timeout=None, phrase_time_limit=8.0)
		if not text:
			print("Didn't catch that.")
			continue
		print(f"Heard: {text}")
		cmd = parse_command(text)
		intent = cmd.get("intent")

		try:
			if intent == "exit":
				responder.say("Goodbye!")
				break
			elif intent == "list_folder":
				folder = cmd.get("folder", ".")
				items = files.list_folder(folder)
				spoken = ", ".join(items[:10]) or "Folder is empty"
				responder.say(f"In {folder}, I found: {spoken}")
			elif intent == "search_files":
				name = cmd.get("name", "")
				if not name:
					responder.say("Please say the file name to search for.")
					continue
				results = files.search_files(name)
				if not results:
					responder.say("I couldn't find any matching files.")
				else:
					responder.say(f"I found {min(len(results), 25)} results. Opening the first one.")
					files.open_file(results[0])
			elif intent == "read_file":
				path = cmd.get("path", "")
				if not path:
					responder.say("Please say the file path to read.")
					continue
				content = files.read_file(path)
				responder.say("Here is the beginning of the file.")
				print("\n===== FILE CONTENT (truncated) =====\n")
				print(content)
				print("\n====================================\n")
			elif intent == "open_file":
				path = cmd.get("path", "")
				if not path:
					responder.say("Please say the file path to open.")
					continue
				files.open_file(path)
				responder.say("Opening the file.")
			elif intent == "time":
				responder.say(time.strftime("It is %I:%M %p"))
			elif intent == "help":
				responder.say(HELP_TEXT)
			elif intent == "chat":
				responder.say("Okay.")
			else:
				responder.say("Sorry, I didn't understand.")
		except Exception as e:
			print("Error:", e)
			traceback.print_exc()
			responder.say("I ran into a problem with that request.")


if __name__ == "__main__":
	main()



