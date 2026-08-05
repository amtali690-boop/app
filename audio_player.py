# ==========================================
# audio_player.py — توليد الصوت (TTS) ومشغل الصوت المخصص + مؤشر الكتابة
# ==========================================
import os
import re
import uuid
import asyncio
import base64
import random
from string import Template

import edge_tts
import streamlit as st
import streamlit.components.v1 as components


def speak(text: str, voice: str, audio_dir: str, rate: str = "+0%") -> str:
    """
    // تم التعديل v10: إضافة معامل rate لدعم النطق البطيء (زر 'كرر ببطء').
    audio_dir: مجلد الصوتيات الخاص بالجلسة الحالية (st.session_state.session_audio_dir).
    """
    if not text or not text.strip():
        return None
    out_path = os.path.join(audio_dir, f"tts_{uuid.uuid4().hex}.mp3")
    clean_text = re.sub(r'[*_#`]', '', text)

    loop = None
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        communicate = edge_tts.Communicate(clean_text, voice, rate=rate)
        loop.run_until_complete(communicate.save(out_path))
        if os.path.exists(out_path):
            return out_path
    except Exception as e:
        print(f"❌ TTS Error: {e}")
    finally:
        if loop is not None:
            loop.close()
    return None


_VOICE_PLAYER_TEMPLATE = Template("""
<!DOCTYPE html>
<html>
<head>
<style>
  html, body { margin:0; padding:4px 0 0 0; background: transparent; font-family: sans-serif; }
  .vp-wrap {
    display: inline-flex; align-items: center; gap: 12px;
    background: linear-gradient(135deg, rgba(56,189,248,0.14), rgba(167,139,250,0.10));
    border: 1px solid rgba(56,189,248,0.28); border-radius: 999px; padding: 8px 16px 8px 8px;
  }
  .vp-btn {
    width: 34px; height: 34px; border-radius: 50%; border: none; cursor: pointer;
    background: linear-gradient(135deg, #38bdf8, #6366f1); color: #fff; font-size: 13px;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 2px 10px rgba(56,189,248,0.35);
  }
  .vp-wave { position: relative; width: ${wave_width}px; height: 28px; cursor: pointer; }
  .vp-bars-bg, .vp-bars-fixed { position: absolute; top: 0; left: 0; width: ${wave_width}px; height: 100%; display: flex; align-items: center; gap: 2px; }
  .vp-bars-bg span { display: block; width: 3px; border-radius: 2px; background: rgba(148,163,184,0.35); }
  .vp-bars-fixed span { display: block; width: 3px; border-radius: 2px; background: linear-gradient(180deg, #38bdf8, #a78bfa); }
  .vp-clip { position: absolute; top: 0; left: 0; height: 100%; width: 0px; overflow: hidden; }
  .vp-time { font-size: 11px; font-weight: 700; color: #94a3b8; min-width: 34px; text-align: right; }
</style>
</head>
<body>
  <div class="vp-wrap" id="wrap">
    <button class="vp-btn" id="btn">&#9658;</button>
    <div class="vp-wave" id="wave">
      <div class="vp-bars-bg">${bars}</div>
      <div class="vp-clip" id="clip"><div class="vp-bars-fixed">${bars}</div></div>
    </div>
    <span class="vp-time" id="timeLabel">0:00</span>
    <audio id="aud" preload="auto" ${autoplay_attr} src="data:audio/mpeg;base64,${b64}"></audio>
  </div>
<script>
  var audio = document.getElementById('aud');
  var btn = document.getElementById('btn');
  var wave = document.getElementById('wave');
  var clip = document.getElementById('clip');
  var timeLabel = document.getElementById('timeLabel');
  var WAVE_WIDTH = ${wave_width};

  function fmt(s) {
    if (!isFinite(s) || s < 0) return '0:00';
    s = Math.round(s);
    var m = Math.floor(s / 60), r = s % 60;
    return m + ':' + (r < 10 ? '0' : '') + r;
  }
  audio.addEventListener('loadedmetadata', function () { timeLabel.textContent = fmt(audio.duration); });
  audio.addEventListener('play', function () { btn.innerHTML = '&#10074;&#10074;'; });
  audio.addEventListener('pause', function () { btn.innerHTML = '&#9658;'; });
  audio.addEventListener('ended', function () { btn.innerHTML = '&#9658;'; clip.style.width = '0px'; });
  audio.addEventListener('timeupdate', function () {
    if (audio.duration) {
      clip.style.width = ((audio.currentTime / audio.duration) * WAVE_WIDTH) + 'px';
      timeLabel.textContent = fmt(audio.currentTime);
    }
  });
  btn.addEventListener('click', function () { if (audio.paused) audio.play(); else audio.pause(); });
  wave.addEventListener('click', function (e) {
    var rect = wave.getBoundingClientRect();
    var frac = Math.min(Math.max((e.clientX - rect.left) / rect.width, 0), 1);
    if (isFinite(audio.duration)) audio.currentTime = frac * audio.duration;
  });
  if (audio.autoplay) audio.play().catch(function(){});
</script>
</body>
</html>
""")


def _wave_bar_heights(seed_key: str, bars: int = 30):
    rng = random.Random(seed_key)
    return [rng.randint(6, 24) for _ in range(bars)]


def render_voice_player(audio_path: str, autoplay: bool):
    if not audio_path or not os.path.exists(audio_path):
        return
    with open(audio_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    heights = _wave_bar_heights(os.path.basename(audio_path))
    bars_html = "".join(f'<span style="height:{h}px"></span>' for h in heights)
    html = _VOICE_PLAYER_TEMPLATE.substitute(wave_width=150, bars=bars_html, autoplay_attr="autoplay" if autoplay else "", b64=b64)
    components.html(html, height=60, scrolling=False)


def render_typing_indicator(slot):
    slot.markdown("""
        <div class="typing-card">
            <span>🤖 AI يفكر ويكتب</span>
            <span class="typing-dots"><span></span><span></span><span></span></span>
        </div>
    """, unsafe_allow_html=True)
