function AboutPage({ onNavigate }) {
    return (
        <section className="content-page about-page" id="about">
            <section className="page-intro">
                <p className="section-label">ABOUT STUDYMATE</p>
                <h1>A little more clarity in every study session.</h1>
                <p>
                    StudyMate is a personal learning workspace built to make it
                    easier to collect notes, stay curious, and understand
                    challenging ideas one step at a time.
                </p>
            </section>

            <section className="about-story">
                <div className="about-story-mark" aria-hidden="true">S</div>
                <div>
                    <p className="form-kicker">BUILT WHILE LEARNING</p>
                    <h2>Made for the whole learning journey.</h2>
                    <p>
                        This project is being built by Aditi Sharma while
                        learning full-stack AI development. It starts with a
                        friendly React study dashboard and is designed to grow
                        into a connected learning companion.
                    </p>
                </div>
            </section>

            <section className="roadmap-section">
                <div className="roadmap-heading">
                    <p className="section-label">THE ROAD AHEAD</p>
                    <h2>Simple today. More helpful over time.</h2>
                </div>
                <div className="roadmap-grid">
                    <article className="roadmap-card">
                        <span className="roadmap-number">01</span>
                        <h3>Organize</h3>
                        <p>Keep study notes, descriptions, and topics together.</p>
                        <span className="roadmap-status">Available now</span>
                    </article>
                    <article className="roadmap-card">
                        <span className="roadmap-number">02</span>
                        <h3>Ask & explore</h3>
                        <p>Use the local AI chat prototype to explore a doubt.</p>
                        <span className="roadmap-status">Interactive prototype</span>
                    </article>
                    <article className="roadmap-card">
                        <span className="roadmap-number">03</span>
                        <h3>Build a knowledge base</h3>
                        <p>
                            Future plans include FastAPI, MySQL, and AI features
                            such as retrieval over your own notes.
                        </p>
                        <span className="roadmap-status">Planned</span>
                    </article>
                </div>
            </section>

            <section className="about-cta">
                <div>
                    <p className="section-label">READY WHEN YOU ARE</p>
                    <h2>What would you like to learn today?</h2>
                </div>
                <div className="about-cta-actions">
                    <button
                        className="primary-btn"
                        type="button"
                        onClick={() => onNavigate("notes")}
                    >
                        Browse my notes
                    </button>
                    <button
                        className="secondary-btn"
                        type="button"
                        onClick={() => onNavigate("ask-ai")}
                    >
                        Ask AI a question
                    </button>
                </div>
            </section>
        </section>
    );
}

export default AboutPage;
