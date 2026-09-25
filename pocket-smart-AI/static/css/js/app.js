const API = "";

const TOKEN_KEY = "pocketsmart_token";


function getToken() {
    return localStorage.getItem(TOKEN_KEY);
}


function setToken(token) {
    localStorage.setItem(
        TOKEN_KEY,
        token
    );
}


function clearToken() {
    localStorage.removeItem(
        TOKEN_KEY
    );
}


async function apiRequest(
    path,
    options = {}
) {
    const headers = new Headers(
        options.headers || {}
    );

    const token = getToken();

    if (token) {
        headers.set(
            "Authorization",
            `Bearer ${token}`
        );
    }

    if (
        options.body &&
        !(options.body instanceof FormData) &&
        !headers.has("Content-Type")
    ) {
        headers.set(
            "Content-Type",
            "application/json"
        );
    }

    const response = await fetch(
        API + path,
        {
            ...options,
            headers,
        }
    );

    let data = {};

    try {
        data = await response.json();
    } catch {
        data = {};
    }

    if (!response.ok) {
        throw new Error(
            data.detail ||
            "Something went wrong."
        );
    }

    return data;
}


function showMessage(
    message,
    type = "info"
) {
    const element =
        document.querySelector(
            "#message"
        );

    if (!element) {
        return;
    }

    element.textContent = message;

    element.className =
        `message ${type}`;

    element.hidden = false;
}


function money(value) {
    return new Intl.NumberFormat(
        "en-IN",
        {
            style: "currency",
            currency: "INR",
            maximumFractionDigits: 0,
        }
    ).format(value);
}


function escapeHtml(value) {
    return String(
        value ?? ""
    ).replace(
        /[&<>'"]/g,
        character => ({
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            "'": "&#39;",
            '"': "&quot;",
        })[character]
    );
}


function requireAuth() {
    if (!getToken()) {
        window.location.href =
            "/login";

        return false;
    }

    return true;
}


function renderRecommendations(
    data
) {
    const root =
        document.querySelector(
            "#results"
        );

    if (!root) {
        return;
    }

    root.innerHTML = `
        <div class="result-head">

            <div>
                <span class="eyebrow">
                    AI PLAN
                </span>

                <h2>
                    ${escapeHtml(
                        data.summary
                    )}
                </h2>
            </div>

            <div class="budget-pill">
                ${money(
                    data.total_estimated_cost
                )}
                /
                ${money(data.budget)}
            </div>

        </div>

        <div class="tips">

            ${(data.tips || [])
                .map(
                    tip => `
                        <div class="tip">
                            ${escapeHtml(
                                tip
                            )}
                        </div>
                    `
                )
                .join("")}

        </div>

        <div class="item-grid">

            ${(data.items || [])
                .map(
                    item => `
                        <article class="item-card">

                            <span>
                                ${escapeHtml(
                                    item.category
                                )}
                            </span>

                            <h3>
                                ${escapeHtml(
                                    item.name
                                )}
                            </h3>

                            <p>
                                ${escapeHtml(
                                    item.description
                                )}
                            </p>

                            ${
                                item.reason
                                    ? `
                                        <p class="reason">
                                            ${escapeHtml(
                                                item.reason
                                            )}
                                        </p>
                                    `
                                    : ""
                            }

                            <strong>
                                ${money(
                                    item.price
                                )}
                            </strong>

                            ${
                                item.url
                                    ? `
                                        <a
                                            href="${escapeHtml(
                                                item.url
                                            )}"
                                            target="_blank"
                                            rel="noopener"
                                        >
                                            View source
                                        </a>
                                    `
                                    : ""
                            }

                        </article>
                    `
                )
                .join("")}

        </div>
    `;
}


function setupAuth() {
    const loginForm =
        document.querySelector(
            "#login-form"
        );

    if (loginForm) {
        loginForm.addEventListener(
            "submit",
            async event => {
                event.preventDefault();

                try {
                    const data =
                        await apiRequest(
                            "/auth/login",
                            {
                                method: "POST",

                                body:
                                    JSON.stringify(
                                        {
                                            username:
                                                loginForm
                                                    .username
                                                    .value,

                                            password:
                                                loginForm
                                                    .password
                                                    .value,
                                        }
                                    ),
                            }
                        );

                    setToken(
                        data.access_token
                    );

                    window.location.href =
                        "/";
                } catch (error) {
                    showMessage(
                        error.message,
                        "error"
                    );
                }
            }
        );
    }


    const registerForm =
        document.querySelector(
            "#register-form"
        );

    if (registerForm) {
        registerForm.addEventListener(
            "submit",
            async event => {
                event.preventDefault();

                try {
                    await apiRequest(
                        "/auth/register",
                        {
                            method: "POST",

                            body:
                                JSON.stringify(
                                    {
                                        username:
                                            registerForm
                                                .username
                                                .value,

                                        email:
                                            registerForm
                                                .email
                                                .value,

                                        password:
                                            registerForm
                                                .password
                                                .value,
                                    }
                                ),
                        }
                    );

                    showMessage(
                        "Account created successfully.",
                        "success"
                    );

                    setTimeout(
                        () => {
                            window.location.href =
                                "/login";
                        },
                        700
                    );

                } catch (error) {
                    showMessage(
                        error.message,
                        "error"
                    );
                }
            }
        );
    }
}


function setupPlanner() {
    const form =
        document.querySelector(
            "[data-planner]"
        );

    if (!form) {
        return;
    }

    form.addEventListener(
        "submit",
        async event => {
            event.preventDefault();

            if (!requireAuth()) {
                return;
            }

            const button =
                form.querySelector(
                    "button[type='submit']"
                );

            button.disabled = true;

            button.textContent =
                "Generating...";

            try {
                let body;

                const options = {
                    method: "POST",
                };

                if (
                    form.dataset.planner ===
                    "jewelry"
                ) {
                    body =
                        new FormData(form);

                    options.body = body;

                } else {
                    const formData =
                        new FormData(form);

                    body =
                        Object.fromEntries(
                            formData.entries()
                        );

                    if (body.budget) {
                        body.budget =
                            Number(
                                body.budget
                            );
                    }

                    if (body.guests) {
                        body.guests =
                            Number(
                                body.guests
                            );
                    }

                    options.body =
                        JSON.stringify(
                            body
                        );
                }

                const data =
                    await apiRequest(
                        `/generate-${form.dataset.planner}`,
                        options
                    );

                renderRecommendations(
                    data
                );

                document
                    .querySelector(
                        "#results"
                    )
                    ?.scrollIntoView({
                        behavior:
                            "smooth",
                    });

            } catch (error) {
                showMessage(
                    error.message,
                    "error"
                );

            } finally {
                button.disabled = false;

                button.textContent =
                    "Generate plan";
            }
        }
    );
}


async function loadHistory() {
    const root =
        document.querySelector(
            "#history-list"
        );

    if (!root) {
        return;
    }

    if (!requireAuth()) {
        return;
    }

    try {
        const data =
            await apiRequest(
                "/history"
            );

        if (!data.length) {
            root.innerHTML =
                "<p class='muted'>No recommendation history yet.</p>";

            return;
        }

        root.innerHTML =
            data
                .map(
                    record => `
                        <article class="history-card">

                            <div>

                                <span class="eyebrow">
                                    ${escapeHtml(
                                        record.planner_type
                                    )}
                                </span>

                                <h3>
                                    Recommendation #${record.id}
                                </h3>

                                <p>
                                    ${new Date(
                                        record.created_at
                                    ).toLocaleString()}
                                </p>

                            </div>

                            <div>
                                ${escapeHtml(
                                    record
                                        .response_data
                                        .summary ||
                                    ""
                                )}
                            </div>

                        </article>
                    `
                )
                .join("");

    } catch (error) {
        showMessage(
            error.message,
            "error"
        );
    }
}


function setupNav() {
    const authLinks =
        document.querySelectorAll(
            "[data-auth-only]"
        );

    authLinks.forEach(
        element => {
            element.style.display =
                getToken()
                    ? "inline-flex"
                    : "none";
        }
    );


    const logout =
        document.querySelector(
            "#logout"
        );

    if (logout) {
        logout.addEventListener(
            "click",
            event => {
                event.preventDefault();

                clearToken();

                window.location.href =
                    "/";
            }
        );
    }
}


document.addEventListener(
    "DOMContentLoaded",
    () => {
        setupAuth();
        setupPlanner();
        setupNav();
        loadHistory();
    }
);