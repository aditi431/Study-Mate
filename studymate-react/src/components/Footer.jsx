function Footer({ onNavigate }) {
    return (
        <footer className="footer--image-design">
            <button
                className="footer-brand footer-link"
                type="button"
                onClick={() => onNavigate("home")}
            >
                StudyMate
            </button>
            <p className="footer__credit">Created by Aditi Sharma</p>
            <p className="footer__credit">© 2026 StudyMate</p>
        </footer>
    );
}

export default Footer;