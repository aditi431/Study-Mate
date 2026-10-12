function Hero({ onAddNoteClick, onNavigate }) {
    return (
        <section className="hero hero-sage" id="home">
            <div className="hero-sage__copy">
                <h1 className="hero-sage__h1">
                    Learn smarter,
                    <br />
                    <span>Study better.</span>
                </h1>

                <p className="hero-sage__body">
                    Organize your study notes, track important topics
                    and build your knowledge — all in one calm space.
                </p>

                <p className="hero-sage__attr">
                    (StudyMate — your personal AI workspace)
                </p>

                <div className="hero-sage__actions">
                    <button
                        className="primary-btn hero-sage__cta-primary"
                        type="button"
                        onClick={onAddNoteClick}
                    >
                        <span aria-hidden="true">+</span> Add New Note
                    </button>
                    <button
                        className="hero-sage__cta-ghost"
                        type="button"
                        onClick={() => onNavigate("ask-ai")}
                    >
                        Ask AI ↗
                    </button>
                </div>
            </div>

            <div className="hero-sage__art" aria-hidden="true">
                <img
                    className="hero-sage__image"
                    src="/study-book-hero.jpe"
                    alt=""
                />
            </div>
        </section>
    );
}

export default Hero;
