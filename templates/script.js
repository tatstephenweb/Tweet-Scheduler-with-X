
    /* ── Navigation ── */
    const views = ['compose','scheduled','drafts','published'];
    function setView(v) {
      views.forEach(id => {
        document.getElementById(`view-${id}`).classList.add('hidden');
        const btn = document.getElementById(`nav-${id}`);
        if (btn) { btn.classList.remove('active'); btn.classList.add('text-ghost'); }
      });
      document.getElementById(`view-${v}`).classList.remove('hidden');
      const activeBtn = document.getElementById(`nav-${v}`);
      if (activeBtn) { activeBtn.classList.add('active'); activeBtn.classList.remove('text-ghost'); }
    }

    /* ── Tabs ── */
    function setTab(t) {
      ['single','thread'].forEach(id => {
        document.getElementById(`panel-${id}`).classList.remove('active');
        document.getElementById(`tab-${id}`).classList.remove('active','text-white','border-pulse');
        document.getElementById(`tab-${id}`).classList.add('text-ghost');
      });
      document.getElementById(`panel-${t}`).classList.add('active');
      document.getElementById(`tab-${t}`).classList.add('active','text-white','border-pulse');
      document.getElementById(`tab-${t}`).classList.remove('text-ghost');
    }

    /* ── Character counter ── */
    function updateChar() {
      const txt = document.getElementById('tweet-text').value;
      const remaining = 280 - txt.length;
      const used = txt.length;
      const pct = Math.min((used / 280) * 100, 100);
      const ring = document.getElementById('char-ring');
      const counter = document.getElementById('char-count');
      ring.style.setProperty('--pct', pct + '%');
      ring.classList.toggle('warn-zone', remaining < 20);
      counter.textContent = remaining;
      counter.classList.toggle('text-warn', remaining < 20);
      counter.classList.toggle('text-ghost', remaining >= 20);
    }

    /* ── Schedule toggle ── */
    let scheduleOpen = false;
    function toggleSchedule() {
      scheduleOpen = !scheduleOpen;
      const row = document.getElementById('schedule-row');
      const label = document.getElementById('sched-btn-label');
      const btn = document.getElementById('schedule-toggle-btn');
      row.classList.toggle('hidden', !scheduleOpen);
      label.textContent = scheduleOpen ? 'Cancel' : 'Schedule';
      btn.classList.toggle('border-pulse', scheduleOpen);
      btn.classList.toggle('text-pulse', scheduleOpen);
      if (scheduleOpen) {
        // Default to tomorrow 9 AM
        const d = new Date(); d.setDate(d.getDate() + 1);
        document.getElementById('sched-date').value = d.toISOString().split('T')[0];
        document.getElementById('sched-time').value = '09:00';
      }
    }

    /* ── Post tweet ── */
    function postTweet() {
      const text = document.getElementById('tweet-text').value.trim();
      if (!text) { showToast('Write something first', true); return; }
      if (scheduleOpen) {
        const date = document.getElementById('sched-date').value;
        const time = document.getElementById('sched-time').value;
        if (!date || !time) { showToast('Pick a date and time', true); return; }
        const formatted = new Date(`${date}T${time}`).toLocaleString('en-NG', {month:'short', day:'numeric', hour:'2-digit', minute:'2-digit'});
        showToast(`Scheduled for ${formatted}`);
        const count = document.getElementById('sched-count');
        count.textContent = parseInt(count.textContent) + 1;
      } else {
        showToast('Tweet posted!');
      }
      document.getElementById('tweet-text').value = '';
      updateChar();
    }

    /* ── AI draft ── */
    const suggestions = [
      "Day 183 of learning in public The one debugging lesson that changed everything for me: the bug is almost never where you think it is.",
      "Hot take: documentation is the most underrated skill in software engineering. A project without clear docs is just a future mystery.",
      "I used to think consistency meant coding every day. Now I think it means showing up — even if it's just 15 minutes of reading docs.",
      "Shipped something today that I broke three times before it worked. That's not failure, that's the job. 🚀",
    ];
    let aiIdx = 0;
    function aiDraft() {
      const box = document.getElementById('ai-box');
      const sugg = document.getElementById('ai-suggestion');
      sugg.textContent = suggestions[aiIdx % suggestions.length];
      aiIdx++;
      box.classList.remove('hidden');
    }
    function useAiSuggestion() {
      const sugg = document.getElementById('ai-suggestion').textContent;
      document.getElementById('tweet-text').value = sugg;
      updateChar();
      document.getElementById('ai-box').classList.add('hidden');
    }

    /* ── Load draft ── */
    function loadDraft() {
      setView('compose');
      const draft = "Day 183 of learning to code in public. Today I fixed a race condition in Quizzer by switching from shared JSON to Flask sessions. Small win, big lesson 🧠";
      document.getElementById('tweet-text').value = draft;
      updateChar();
    }

    /* ── Thread: add tweet ── */
    function addThreadTweet() {
      const container = document.getElementById('thread-container');
      const n = container.querySelectorAll('.thread-item').length + 1;
      const div = document.createElement('div');
      div.className = 'flex gap-3 thread-item';
      div.innerHTML = `
        <div class="flex flex-col items-center">
          <div class="w-9 h-9 rounded-full bg-gradient-to-br from-sky to-pulse flex items-center justify-center text-xs font-mono font-500 text-ink shrink-0">T</div>
          <div class="thread-connector flex-1 mt-2 ml-px" style="min-height:24px"></div>
        </div>
        <div class="flex-1 pb-3">
          <p class="text-sm font-500 mb-2">@tat_codes</p>
          <textarea class="compose-area w-full bg-transparent text-white text-base resize-none placeholder-muted border border-border rounded-lg p-3 font-body leading-relaxed min-h-[80px]" placeholder="Tweet ${n}…" maxlength="280"></textarea>
          <div class="flex justify-end mt-1.5"><span class="text-xs font-mono text-muted">280</span></div>
        </div>`;
      container.appendChild(div);
    }

    /* ── Toast ── */
    let toastTimer;
    function showToast(msg, isError = false) {
      const t = document.getElementById('toast');
      const m = document.getElementById('toast-msg');
      const icon = t.querySelector('i');
      m.textContent = msg;
      icon.className = isError ? 'fa-solid fa-circle-exclamation text-warn' : 'fa-solid fa-circle-check text-pulse';
      t.classList.remove('hidden');
      clearTimeout(toastTimer);
      toastTimer = setTimeout(() => t.classList.add('hidden'), 3000);
    }

    // Init date placeholder
    const tomorrow = new Date(); tomorrow.setDate(tomorrow.getDate()+1);
    if (document.getElementById('sched-date')) {
      document.getElementById('sched-date').min = tomorrow.toISOString().split('T')[0];
    }