
 // click profile picture
        let img = document.querySelector(".profile-image");
        let about = document.querySelector("#aboutme");

        img.addEventListener('click', () => {
            about.scrollIntoView({ behavior: "smooth" });
        });

        // Smooth scrolling for anchor links
        document.querySelectorAll('nav ul li a').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault(); // Prevent default anchor click behavior

                const target = document.querySelector(this.getAttribute('href')); // Get the target section
                target.scrollIntoView({ behavior: 'smooth', block: 'start' }); // Scroll smoothly to the section
            });
        });
        // mobile manu
        document.addEventListener("DOMContentLoaded", () => {
        const menuToggle = document.getElementById('menu-toggle');
        const navList = document.getElementById('nav-list');

        menuToggle.addEventListener('click', () => {
            navList.classList.toggle('active');

            menuToggle.innerHTML = navList.classList.contains('active') 
            ? '<i class="fas fa-times"></i>' 
            : '<i class="fas fa-bars"></i>';
        });
    });



        // Fade-in effect for sections
        const sections = document.querySelectorAll('.scroll-reveal');
        const options = {
            root: null,
            threshold: 0.1,
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        }, options);



// Update copyright year automatically
    
    document.getElementById('current-year').textContent = new Date().getFullYear();

    // Smooth scroll for footer links
    document.querySelectorAll('.footer-menu a').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

// effect..............

// Cache container element
const container = document.querySelector('.container');

// Create a document fragment to batch DOM operations
const fragment = document.createDocumentFragment();

// Create a single stylesheet for all animations
const styleSheet = document.createElement('style');
styleSheet.textContent = `
  @keyframes move-up {
    0% { transform: translateY(0); opacity: 1; }
    100% { transform: translateY(-120vh); opacity: 0; }
  }
`;
document.head.appendChild(styleSheet);

// Generate all circles at once
for (let i = 0; i < 100; i++) {
  const circleContainer = document.createElement('div');
  circleContainer.className = 'circle-container';
  
  const circle = document.createElement('div');
  circle.className = 'circle';

  // Set random properties in one pass
  const size = Math.floor(Math.random() * 9) + 2;
  Object.assign(circle.style, {
    width: `${size}px`,
    height: `${size}px`
  });

  Object.assign(circleContainer.style, {
    left: `${Math.random() * 100}vw`,
    top: `${100 + Math.random() * 10}vh`,
    animation: `move-up ${20 + Math.random() * 5}s linear ${Math.random() * 20}s infinite`
  });

  circleContainer.appendChild(circle);
  fragment.appendChild(circleContainer);
}

// Single DOM insertion
container.appendChild(fragment);

// connect
