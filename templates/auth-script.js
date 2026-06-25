
    function setAuthTab(tab) {
      const isLogin = tab === 'login';

      document.getElementById('tab-login').classList.toggle('active', isLogin);
      document.getElementById('tab-signup').classList.toggle('active', !isLogin);

      document.getElementById('form-login').classList.toggle('active', isLogin);
      document.getElementById('form-signup').classList.toggle('active', !isLogin);

      document.getElementById('form-heading').textContent = isLogin ? 'Welcome back' : 'Create your account';
      document.getElementById('form-subheading').textContent = isLogin
        ? 'Log in to manage your posts.'
        : 'Start scheduling tweets in minutes.';

      document.getElementById('switch-line').innerHTML = isLogin
        ? `Don't have an account? <button onclick="setAuthTab('signup')" class="text-pulse font-500 hover:underline">Sign up</button>`
        : `Already have an account? <button onclick="setAuthTab('login')" class="text-pulse font-500 hover:underline">Log in</button>`;
    }

    function togglePw(id, btn) {
      const input = document.getElementById(id);
      const icon = btn.querySelector('i');
      const show = input.type === 'password';
      input.type = show ? 'text' : 'password';
      icon.className = show ? 'fa-regular fa-eye-slash' : 'fa-regular fa-eye';
    }

    function checkStrength(val) {
      const segs = [document.getElementById('seg-1'), document.getElementById('seg-2'), document.getElementById('seg-3')];
      segs.forEach(s => s.className = 'strength-seg h-1 rounded-full flex-1');

      let score = 0;
      if (val.length >= 8) score++;
      if (/[A-Z]/.test(val) && /[0-9]/.test(val)) score++;
      if (val.length >= 12 && /[^A-Za-z0-9]/.test(val)) score++;

      const labels = ['Use 8+ characters', 'Weak', 'Good', 'Strong'];
      for (let i = 0; i < score; i++) segs[i].classList.add(`on-${score}`);
      document.getElementById('strength-label').textContent = val.length === 0 ? 'Use 8+ characters' : labels[score];
    }

    function handleSubmit(e, type) {
      e.preventDefault();
      const form = e.target;
      if (!form.checkValidity()) { form.reportValidity(); return false; }

      const btnText = document.getElementById(`${type}-btn-text`);
      const spinner = document.getElementById(`${type}-spinner`);
      btnText.classList.add('hidden');
      spinner.classList.remove('hidden');

      // Replace this block with a real fetch() call to your Flask /auth endpoint
      setTimeout(() => {
        btnText.classList.remove('hidden');
        spinner.classList.add('hidden');
        showToast(type === 'login' ? 'Logged in! Redirecting…' : 'Account created! Connect your X account next.');
      }, 900);

      return false;
    }

    function handleX() {
      showToast('Redirecting to X authorization…');
    }

    let toastTimer;
    function showToast(msg) {
      const t = document.getElementById('toast');
      document.getElementById('toast-msg').textContent = msg;
      t.classList.remove('hidden');
      clearTimeout(toastTimer);
      toastTimer = setTimeout(() => t.classList.add('hidden'), 3000);
    }