// script.js

// Highlight active link in navbar
const navLinks = document.querySelectorAll('.nav-links li a');
navLinks.forEach(link => {
    link.addEventListener('click', () => {
        navLinks.forEach(nav => nav.classList.remove('active'));
        link.classList.add('active');
    });
});

// Scroll-to-Top Button
const scrollToTopBtn = document.createElement('button');
scrollToTopBtn.textContent = "↑";
scrollToTopBtn.classList.add('scroll-to-top');
document.body.appendChild(scrollToTopBtn);

scrollToTopBtn.style.cssText = `
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    padding: 0.5rem 1rem;
    background: #ff7b54;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
    display: none;
    z-index: 1000;
`;

window.addEventListener('scroll', () => {
    if (window.scrollY > 300) {
        scrollToTopBtn.style.display = 'block';
    } else {
        scrollToTopBtn.style.display = 'none';
    }
});

scrollToTopBtn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
});

// Receipt Upload Preview
const receiptInput = document.querySelector('#receipt-upload');
const receiptPreview = document.querySelector('#receipt-preview');

if (receiptInput && receiptPreview) {
    receiptInput.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                receiptPreview.src = e.target.result;
                receiptPreview.style.display = 'block';
            };
            reader.readAsDataURL(file);
        }
    });
}

// FAQ Accordion
// Toggle FAQ answers
const faqItems = document.querySelectorAll('.faq-item');

faqItems.forEach(item => {
    const question = item.querySelector('.faq-question');
    question.addEventListener('click', () => {
        // Close all open FAQs
        faqItems.forEach(faq => {
            if (faq !== item) faq.classList.remove('active');
            const answer = faq.querySelector('.faq-answer');
            answer.style.maxHeight = faq.classList.contains('active') ? answer.scrollHeight + 'px' : '0';
        });

        // Toggle current FAQ
        item.classList.toggle('active');
        const answer = item.querySelector('.faq-answer');
        answer.style.maxHeight = item.classList.contains('active') ? answer.scrollHeight + 'px' : '0';
    });
});