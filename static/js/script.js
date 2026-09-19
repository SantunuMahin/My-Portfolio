// ============================================================
//  PORTFOLIO MAIN SCRIPT (ENHANCED SPA PJAX ARCHITECTURE)
//  - Sidebar mobile toggle & sticky contacts
//  - Navbar tab switching & sliding pill indicator
//  - Project category filtering
//  - SPA PJAX Router with dynamic lifecycle hooks
//  - Reading progress indicator
//  - Lenis Smooth Scroll Integration
// ============================================================

// Initialize Lenis Smooth Scroll globally
if (typeof Lenis !== 'undefined') {
  window.lenisInstance = new Lenis({
    autoRaf: true,
    duration: 1.2,
    easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)), // easeOutQuart
    smoothWheel: true,
  });
}

function initPortfolio() {
  /* ---- Sidebar mobile toggle ---- */
  const sidebar    = document.querySelector('[data-sidebar]');
  const contactsToggle = document.getElementById('sidebar-contacts-toggle');
  const sidebarMore = sidebar?.querySelector('.sidebar-info-more');

  if (contactsToggle && sidebarMore) {
    if (!contactsToggle.dataset.hasListener) {
      contactsToggle.addEventListener('click', () => {
        const isOpen = sidebarMore.classList.toggle('active');
        contactsToggle.setAttribute('aria-expanded', String(isOpen));
        const label = contactsToggle.querySelector('.toggle-label');
        if (label) label.textContent = isOpen ? 'Hide Contacts' : 'Show Contacts';
      });
      contactsToggle.dataset.hasListener = 'true';
    }
  }

  /* ---- Navbar tab switching on home page ---- */
  const navLinks   = document.querySelectorAll('[data-nav-link]');
  const articles   = document.querySelectorAll('[data-page]');

  navLinks.forEach(link => {
    if (link.dataset.hasTabListener) return;
    link.dataset.hasTabListener = 'true';

    link.addEventListener('click', e => {
      const target = link.dataset.target;
      if (!target) return; // Regular links handled by PJAX router

      // Auto-collapse mobile contacts toggle when navigating between tabs
      if (window.innerWidth < 1024 && contactsToggle && sidebarMore && sidebarMore.classList.contains('active')) {
        sidebarMore.classList.remove('active');
        contactsToggle.setAttribute('aria-expanded', 'false');
        const label = contactsToggle.querySelector('.toggle-label');
        if (label) label.textContent = 'Show Contacts';
      }

      if (window.location.pathname !== '/') {
        e.preventDefault();
        navigateTo(`/#${target}`);
        return;
      }

      const activeArticle = document.querySelector('article.active');
      const targetEl = document.querySelector(`[data-page="${target}"]`);

      if (activeArticle && targetEl && activeArticle !== targetEl) {
        activeArticle.classList.add('tab-fade-out');

        navLinks.forEach(l => {
          if (l.dataset.target === target) {
            l.classList.add('active');
          } else {
            l.classList.remove('active');
          }
        });
        moveNavbarIndicator();

        setTimeout(() => {
          activeArticle.classList.remove('active', 'tab-fade-out');
          targetEl.classList.add('active');

          const reveals = targetEl.querySelectorAll('.reveal-on-scroll');
          reveals.forEach(el => el.classList.add('revealed'));

          const timelineItems = targetEl.querySelectorAll('.timeline-item');
          timelineItems.forEach(el => el.classList.add('reveal'));

          if (window.innerWidth < 1024) {
            if (target === 'about') {
              if (window.lenisInstance) {
                window.lenisInstance.scrollTo(0, { duration: 0.7 });
              } else {
                window.scrollTo({ top: 0, behavior: 'smooth' });
              }
            } else {
              const headerEl = targetEl.querySelector('header') || targetEl;
              if (window.lenisInstance) {
                window.lenisInstance.scrollTo(headerEl, { offset: -75, duration: 0.7 });
              } else {
                const headerRect = headerEl.getBoundingClientRect();
                window.scrollTo({ top: window.scrollY + headerRect.top - 75, behavior: 'smooth' });
              }
            }
          } else {
            if (window.scrollY > 80) {
              if (window.lenisInstance) {
                window.lenisInstance.scrollTo(0, { duration: 0.8 });
              } else {
                window.scrollTo({ top: 0, behavior: 'smooth' });
              }
            }
          }

          history.pushState({ url: `/#${target}` }, document.title, `/#${target}`);
        }, 180);
      } else if (targetEl) {
        navLinks.forEach(l => {
          if (l.dataset.target === target) {
            l.classList.add('active');
          } else {
            l.classList.remove('active');
          }
        });
        articles.forEach(a => a.classList.remove('active'));
        targetEl.classList.add('active');

        const reveals = targetEl.querySelectorAll('.reveal-on-scroll');
        reveals.forEach(el => el.classList.add('revealed'));

        const timelineItems = targetEl.querySelectorAll('.timeline-item');
        timelineItems.forEach(el => el.classList.add('reveal'));

        if (window.innerWidth < 1024) {
          if (target === 'about') {
            if (window.lenisInstance) {
              window.lenisInstance.scrollTo(0, { duration: 0.7 });
            } else {
              window.scrollTo({ top: 0, behavior: 'smooth' });
            }
          } else {
            const headerEl = targetEl.querySelector('header') || targetEl;
            if (window.lenisInstance) {
              window.lenisInstance.scrollTo(headerEl, { offset: -75, duration: 0.7 });
            } else {
              const headerRect = headerEl.getBoundingClientRect();
              window.scrollTo({ top: window.scrollY + headerRect.top - 75, behavior: 'smooth' });
            }
          }
        }

        moveNavbarIndicator();
        history.pushState({ url: `/#${target}` }, document.title, `/#${target}`);
      }
    });
  });

  /* ---- Project category filter ---- */
  const filterBtns  = document.querySelectorAll('[data-filter-btn]');
  const projectItems = document.querySelectorAll('[data-filter-item]');

  filterBtns.forEach(btn => {
    if (btn.dataset.hasFilterListener) return;
    btn.dataset.hasFilterListener = 'true';

    btn.addEventListener('click', () => {
      const filter = btn.dataset.filter;

      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      projectItems.forEach(item => {
        if (filter === 'all' || item.dataset.category === filter) {
          item.classList.remove('hidden');
          setTimeout(() => item.classList.add('reveal'), 50);
        } else {
          item.classList.add('hidden');
          item.classList.remove('reveal');
        }
      });
    });
  });

  // Setup Scroll Reveal IntersectionObserver
  setupScrollReveal();

  // Setup scroll depth compact header mode
  setupScrollCompact();

  // Setup reading progress indicator
  setupReadingProgress();

  // Automatically update navbar active highlight
  updateNavbarActiveState();
  
  // Position sliding indicator
  setTimeout(moveNavbarIndicator, 80);

  /* ---- Mobile Off-Canvas Drawer Toggle & Gestures ---- */
  const navbar = document.querySelector('.navbar');
  const hamburgerBtn = document.getElementById('hamburgerBtn');
  const mobileDrawer = document.getElementById('mobileMenuDrawer');
  const drawerCloseBtn = document.getElementById('drawerCloseBtn');
  const mobileBackdrop = document.getElementById('mobileNavBackdrop');
  const navLinksList = document.querySelectorAll('.navbar-link');

  const openMobileMenu = () => {
    navbar?.classList.add('open');
    mobileDrawer?.classList.add('open');
    mobileDrawer?.setAttribute('aria-hidden', 'false');
    hamburgerBtn?.classList.add('open');
    hamburgerBtn?.setAttribute('aria-expanded', 'true');
    mobileBackdrop?.classList.add('active');
    document.body.classList.add('mobile-menu-open');
  };

  const closeMobileMenu = () => {
    navbar?.classList.remove('open');
    mobileDrawer?.classList.remove('open');
    mobileDrawer?.setAttribute('aria-hidden', 'true');
    hamburgerBtn?.classList.remove('open');
    hamburgerBtn?.setAttribute('aria-expanded', 'false');
    mobileBackdrop?.classList.remove('active');
    document.body.classList.remove('mobile-menu-open');
  };

  const toggleMobileMenu = () => {
    const isOpen = mobileDrawer ? mobileDrawer.classList.contains('open') : navbar?.classList.contains('open');
    if (isOpen) {
      closeMobileMenu();
    } else {
      openMobileMenu();
    }
  };

  if (hamburgerBtn) {
    if (!hamburgerBtn.dataset.hasListener) {
      hamburgerBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        toggleMobileMenu();
      });
      hamburgerBtn.dataset.hasListener = 'true';
    }

    if (drawerCloseBtn && !drawerCloseBtn.dataset.hasListener) {
      drawerCloseBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        closeMobileMenu();
      });
      drawerCloseBtn.dataset.hasListener = 'true';
    }

    if (mobileBackdrop && !mobileBackdrop.dataset.hasListener) {
      mobileBackdrop.addEventListener('click', closeMobileMenu);
      mobileBackdrop.dataset.hasListener = 'true';
    }

    navLinksList.forEach(link => {
      if (!link.dataset.hasMenuCloseListener) {
        link.addEventListener('click', closeMobileMenu);
        link.dataset.hasMenuCloseListener = 'true';
      }
    });

    // Only attach swipe-to-close on touch devices / mobile viewports
    if (mobileDrawer && !mobileDrawer.dataset.hasSwipeListener && window.matchMedia('(max-width: 1024px)').matches) {
      let startX = 0;
      let startY = 0;
      mobileDrawer.addEventListener('touchstart', (e) => {
        startX = e.touches[0].clientX;
        startY = e.touches[0].clientY;
      }, { passive: true });

      mobileDrawer.addEventListener('touchend', (e) => {
        const endX = e.changedTouches[0].clientX;
        const endY = e.changedTouches[0].clientY;
        const diffX = endX - startX;
        const diffY = Math.abs(endY - startY);
        // Swiping right to close
        if (diffX > 60 && diffX > diffY) {
          closeMobileMenu();
        }
      }, { passive: true });
      mobileDrawer.dataset.hasSwipeListener = 'true';
    }


    if (!document.hasOutsideClickListener) {
      document.addEventListener('click', (e) => {
        if ((navbar?.classList.contains('open') || mobileDrawer?.classList.contains('open')) &&
            !mobileDrawer?.contains(e.target) &&
            !hamburgerBtn?.contains(e.target)) {
          closeMobileMenu();
        }
      });
      document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
          closeMobileMenu();
        }
      });
      document.hasOutsideClickListener = true;
    }
  }

  // Trigger app-specific lifecycle initializers if their elements are present
  if (document.getElementById('kanbanBoard') && typeof window.initTracker === 'function') {
    window.initTracker();
  }
}

/* ---- Dark/Light theme toggle (persistent for multiple triggers) ---- */
function initThemeToggle() {
  const themeToggles = document.querySelectorAll('.theme-toggle');
  themeToggles.forEach(themeToggle => {
    if (!themeToggle.dataset.hasListener) {
      themeToggle.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('portfolio-theme', newTheme);
      });
      themeToggle.dataset.hasListener = 'true';
    }
  });
}

/* ---- Sliding active link pill indicator ---- */
function moveNavbarIndicator() {
  const activeLink = document.querySelector('.navbar-list .navbar-link.active') || document.querySelector('.navbar-link.active');
  const indicator = document.getElementById('navbarIndicator');
  if (activeLink && indicator && activeLink.offsetParent) {
    indicator.style.left = `${activeLink.offsetLeft}px`;
    indicator.style.width = `${activeLink.offsetWidth}px`;
  }
}

/* ---- Scroll Reveal (Intersection Observer) ---- */
function setupScrollReveal() {
  const reveals = document.querySelectorAll('.reveal-on-scroll');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('revealed');
        // Disconnect once revealed — saves memory on long pages
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });

  reveals.forEach(el => observer.observe(el));

  // Stagger cards in lists
  const cards = document.querySelectorAll('.blog-card, .pin-board-card');
  cards.forEach((card, i) => {
    setTimeout(() => card.classList.add('reveal'), 50 * i);
  });
}


/* ---- Reading Progress Bar ---- */
function setupReadingProgress() {
  const bar = document.getElementById('readingProgressBar');
  if (!bar) return;

  const updateProgress = () => {
    const scrollH = document.documentElement.scrollHeight - window.innerHeight;
    if (scrollH > 100) {
      const scrolled = (window.scrollY / scrollH) * 100;
      bar.style.width = `${Math.min(100, Math.max(0, scrolled))}%`;
      bar.style.opacity = window.scrollY > 40 ? '1' : '0';
    } else {
      bar.style.width = '0%';
      bar.style.opacity = '0';
    }
  };

  window.removeEventListener('scroll', updateProgress);
  window.addEventListener('scroll', updateProgress, { passive: true });
  updateProgress();
}

/* ---- Scroll Compact Header ---- */
function setupScrollCompact() {
  const nav = document.querySelector('.navbar');
  if (!nav) return;
  window.addEventListener('scroll', () => {
    if (window.scrollY > 80) {
      nav.classList.add('compact');
    } else {
      nav.classList.remove('compact');
    }
    moveNavbarIndicator();
  }, { passive: true });
}

/* ---- Update Navbar Active State ---- */
function updateNavbarActiveState() {
  const path = window.location.pathname;
  const hash = window.location.hash.replace('#', '');
  const navLinks = document.querySelectorAll('.navbar-link');

  navLinks.forEach(l => l.classList.remove('active'));

  if (path === '/' || path === '') {
    const activeTarget = (hash && /^[a-zA-Z0-9_-]+$/.test(hash)) ? hash : 'about';
    const activeLinks = document.querySelectorAll(`.navbar-link[data-target="${activeTarget}"]`);
    activeLinks.forEach(l => l.classList.add('active'));

    const articles = document.querySelectorAll('[data-page]');
    articles.forEach(a => a.classList.remove('active'));
    const targetEl = document.querySelector(`[data-page="${activeTarget}"]`);
    if (targetEl) {
      targetEl.classList.add('active');
      const reveals = targetEl.querySelectorAll('.reveal-on-scroll');
      reveals.forEach(el => el.classList.add('revealed'));
      
      const timelineItems = targetEl.querySelectorAll('.timeline-item');
      timelineItems.forEach(el => el.classList.add('reveal'));

      if (hash && hash !== 'about') {
        setTimeout(() => {
          const headerEl = targetEl.querySelector('header') || targetEl;
          if (window.lenisInstance) {
            window.lenisInstance.scrollTo(headerEl, { offset: -80, duration: 1.0 });
          } else {
            headerEl.scrollIntoView({ behavior: 'smooth' });
          }
        }, 200);
      }
    }
  } else {
    navLinks.forEach(link => {
      const href = link.getAttribute('href');
      if (href && href !== '/' && (path.startsWith(href) || (href.includes('/pins/') && path.startsWith('/pins')) || (href.includes('/books/') && path.startsWith('/books')) || (href.includes('/blog/') && path.startsWith('/blog')) || (href.includes('/tasks/') && path.startsWith('/tasks')))) {
        link.classList.add('active');
      }
    });
  }
  moveNavbarIndicator();
}

/* ================================================================
   SPA PJAX ROUTER
   ================================================================ */

function executePageScripts(doc) {
  if (!doc) return;
  document.querySelectorAll('.pjax-dynamic-script').forEach(el => el.remove());

  const scripts = doc.querySelectorAll('script');
  scripts.forEach(oldScript => {
    const src = oldScript.getAttribute('src') || '';
    if (src.includes('script.js') || src.includes('ionicons') || src.includes('lenis')) {
      return;
    }

    const newScript = document.createElement('script');
    Array.from(oldScript.attributes).forEach(attr => {
      newScript.setAttribute(attr.name, attr.value);
    });
    
    if (oldScript.src) {
      newScript.src = oldScript.src;
    } else {
      newScript.textContent = oldScript.textContent;
    }

    newScript.classList.add('pjax-dynamic-script');
    document.body.appendChild(newScript);
  });
}

// Active AbortController: cancels stale in-flight PJAX fetches on rapid navigation
let _pjaxAbortController = null;

async function navigateTo(url, pushToHistory = true) {
  const viewport = document.getElementById('spa-content-viewport');
  if (!viewport) return;

  // Abort any previous in-flight navigation request (race condition fix)
  if (_pjaxAbortController) {
    _pjaxAbortController.abort();
  }
  _pjaxAbortController = new AbortController();
  const { signal } = _pjaxAbortController;

  viewport.classList.add('pjax-fade-out');

  try {
    const response = await fetch(url, { signal });
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const htmlText = await response.text();

    const parser = new DOMParser();
    const doc = parser.parseFromString(htmlText, 'text/html');
    const newViewport = doc.getElementById('spa-content-viewport');

    if (!newViewport) {
      window.location.href = url;
      return;
    }

    // Wait for fade-out to finish
    await new Promise(r => setTimeout(r, 140));

    viewport.outerHTML = newViewport.outerHTML;

    const updatedViewport = document.getElementById('spa-content-viewport');
    if (updatedViewport) {
      updatedViewport.classList.remove('pjax-fade-out');
      updatedViewport.classList.add('pjax-fade-in');
      setTimeout(() => updatedViewport.classList.remove('pjax-fade-in'), 280);
    }

    document.title = doc.title;

    if (pushToHistory) {
      history.pushState({ url }, doc.title, url);
    }

    if (window.lenisInstance) {
      window.lenisInstance.scrollTo(0, { immediate: true });
    } else {
      window.scrollTo(0, 0);
    }

    executePageScripts(doc);
    initPortfolio();

  } catch (error) {
    if (error.name === 'AbortError') {
      // Navigation superseded by a newer click — silently ignore
      return;
    }
    console.error('PJAX navigation error, falling back to full navigation:', error);
    window.location.href = url;
  } finally {
    _pjaxAbortController = null;
  }
}


// Intercept clicks on links for PJAX routing
document.addEventListener('click', e => {
  const link = e.target.closest('a');
  if (!link) return;

  const url = link.getAttribute('href');
  if (!url) return;

  // Skip external links, anchors, downloads, media, admin
  if (
    url.startsWith('http://') || 
    url.startsWith('https://') || 
    url.startsWith('mailto:') || 
    url.startsWith('tel:') || 
    url.startsWith('#') || 
    link.target === '_blank' || 
    link.hasAttribute('download') ||
    url.includes('/admin/') ||
    url.startsWith('/media/')
  ) {
    return;
  }

  e.preventDefault();
  navigateTo(url);
});

// Handle Back/Forward history navigation
window.addEventListener('popstate', e => {
  const url = e.state?.url || window.location.pathname + window.location.search + window.location.hash;
  navigateTo(url, false);
});

// Reposition sliding active indicator and auto-close drawer on resize
// Debounced to prevent layout thrashing on every resize pixel
let _resizeTimer = null;
window.addEventListener('resize', () => {
  clearTimeout(_resizeTimer);
  _resizeTimer = setTimeout(() => {
    if (window.innerWidth > 1024) {
      document.querySelector('.navbar')?.classList.remove('open');
      document.getElementById('mobileMenuDrawer')?.classList.remove('open');
      document.getElementById('mobileMenuDrawer')?.setAttribute('aria-hidden', 'true');
      const hBtn = document.getElementById('hamburgerBtn');
      hBtn?.classList.remove('open');
      hBtn?.setAttribute('aria-expanded', 'false');
      document.getElementById('mobileNavBackdrop')?.classList.remove('active');
      document.body.classList.remove('mobile-menu-open');
    }
    moveNavbarIndicator();
  }, 150);
});


// Setup on initial load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    initPortfolio();
    initThemeToggle();
  });
} else {
  initPortfolio();
  initThemeToggle();
}
