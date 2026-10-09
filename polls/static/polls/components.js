document.addEventListener("alpine:init", () => {
    Alpine.data("pollShowcase", () => {
        // Keep Chart.js outside Alpine's reactive state: Chart has circular references.
        let chart = null;
        let request = null;
        let destroyed = false;
        const colors = ["#19846b", "#ee9b7e", "#d9b75e", "#8282b5", "#72a9bd"];
        const loadError = "We couldn't load the polls. Please try again.";

        return {
            polls: [],
            search: "",
            loading: true,
            error: "",
            selectedPoll: null,
            detailPoll: null,
            chartType: "bar",

            init() {
                this.loadPolls();
            },

            get filteredPolls() {
                const query = this.search.trim().toLocaleLowerCase();
                return this.polls.filter((poll) =>
                    poll.question_text.toLocaleLowerCase().includes(query),
                );
            },

            get totalVotes() {
                return this.polls.reduce((total, poll) => total + this.voteCount(poll), 0);
            },

            async loadPolls() {
                request?.abort();
                const currentRequest = new AbortController();
                request = currentRequest;
                this.loading = true;
                this.error = "";

                try {
                    const response = await fetch(this.$root.dataset.apiUrl, {
                        headers: { Accept: "application/json" },
                        cache: "no-store",
                        signal: currentRequest.signal,
                    });
                    const polls = response.ok ? await response.json() : null;
                    if (destroyed || currentRequest.signal.aborted) return;
                    if (!Array.isArray(polls)) {
                        this.error = loadError;
                        return;
                    }

                    const selectedId = this.selectedPoll?.id;
                    this.polls = polls;
                    this.selectedPoll = polls.find((poll) => poll.id === selectedId) ?? polls[0] ?? null;
                    if (this.detailPoll) {
                        this.detailPoll = polls.find((poll) => poll.id === this.detailPoll.id) ?? null;
                        if (!this.detailPoll) this.$refs.details.close();
                    }
                    await this.$nextTick();
                    if (!destroyed && !currentRequest.signal.aborted) this.renderChart();
                } catch (error) {
                    if (!destroyed && error.name !== "AbortError") {
                        this.error = loadError;
                    }
                } finally {
                    if (!destroyed && request === currentRequest) this.loading = false;
                }
            },

            async selectPoll(poll) {
                this.selectedPoll = poll;
                await this.$nextTick();
                if (!destroyed) this.renderChart();
            },

            openDetails(poll) {
                this.detailPoll = poll;
                this.$nextTick(() => {
                    if (!destroyed) this.$refs.details.showModal();
                });
            },

            voteUrl(poll) {
                return poll ? this.$root.dataset.detailUrl.replace(/\/0\/$/, `/${poll.id}/`) : "#";
            },

            voteCount(poll) {
                return poll?.choices.reduce((total, choice) => total + choice.votes, 0) ?? 0;
            },

            voteShare(choice, poll) {
                const total = this.voteCount(poll);
                return total ? Math.round((choice.votes / total) * 100) : 0;
            },

            formatDate(date) {
                return new Intl.DateTimeFormat(undefined, {
                    month: "short", day: "numeric", year: "numeric",
                }).format(new Date(date));
            },

            formatNumber(number) {
                return new Intl.NumberFormat().format(number);
            },

            colorFor(index) {
                return colors[index % colors.length];
            },

            renderChart() {
                chart?.destroy();
                chart = null;
                const poll = this.selectedPoll;
                if (!poll?.choices.length) return;
                if (this.chartType === "doughnut" && !this.voteCount(poll)) return;

                const isBar = this.chartType === "bar";
                chart = new Chart(this.$refs.chart, {
                    type: this.chartType,
                    data: {
                        labels: poll.choices.map((choice) => choice.choice_text),
                        datasets: [{
                            label: "Votes",
                            data: poll.choices.map((choice) => choice.votes),
                            backgroundColor: poll.choices.map((_, index) => this.colorFor(index)),
                            borderWidth: 0,
                            borderRadius: isBar ? 6 : 0,
                        }],
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        animation: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? false : { duration: 350 },
                        indexAxis: "y",
                        plugins: {
                            legend: { display: false },
                            tooltip: { callbacks: {
                                label: (context) => `${this.formatNumber(context.raw)} votes`,
                            } },
                        },
                        ...(isBar ? {
                            scales: {
                                x: {
                                    beginAtZero: true,
                                    ticks: { precision: 0, color: "#63756e" },
                                    grid: { color: "#edf0eb" },
                                    border: { display: false },
                                },
                                y: {
                                    ticks: { color: "#263d33" },
                                    grid: { display: false },
                                    border: { display: false },
                                },
                            },
                        } : { cutout: "72%" }),
                    },
                });
            },

            destroy() {
                destroyed = true;
                request?.abort();
                chart?.destroy();
            },
        };
    });
});
