import { Widget } from "../core/widget.js";
import { eventBus } from "../core/event-bus.js";
import { Events } from "../core/events.js";

export class OSD extends Widget {
    constructor(selector = "#osd") {
        super();

        this.selector = selector;
        this.root = null;

        this.channelNumber = null;
        this.channelName = null;
        this.title = null;
        this.logo = null;
        this.progressFill = null;
        this.start = null;
        this.stop = null;

        this.hideTimer = null;
        this.unsubscribe = null;
    }

    initialize() {
        this.root = document.querySelector(this.selector);
        console.log("OSD initialisiert:", this.root);
        if (!this.root) {
            console.warn("OSD: Element wurde nicht gefunden.");
            return;
        }

        this.channelNumber = this.root.querySelector(
            "#osd-channel-number"
        );
        this.channelName = this.root.querySelector(
            "#osd-channel-name"
        );
        this.title = this.root.querySelector(
            "#osd-title"
        );
        this.progressFill = this.root.querySelector(
            "#osd-progress-fill"
        );
        this.start = this.root.querySelector(
            "#osd-start"
        );
        this.stop = this.root.querySelector(
            "#osd-stop"
        );

        this.unsubscribe = eventBus.on(
            Events.OSD_SHOW,
            (payload) => this.show(payload)
        );
        this.logo = this.root.querySelector(
            "#osd-channel-logo"
        );
        this.logo?.addEventListener("error", () => {
            this.logo.hidden = true;
        });
        this.fullscreenButton =
        this.root.querySelector("#osd-fullscreen");

        this.fullscreenButton?.addEventListener(
           "click",
           () => this.toggleFullscreen()
        );
    }
    destroy() {
        this.unsubscribe?.();

        if (this.hideTimer !== null) {
            window.clearTimeout(this.hideTimer);
            this.hideTimer = null;
        }
    }

show(payload) {
    if (!this.root || !payload) {
        return;
    }

    const channel = payload.channel ?? payload;
    const duration = Number(payload.duration) || 5000;

    if (!channel) {
        return;
    }

    this.channelNumber.textContent =
        Number.isFinite(channel.number)
            ? String(channel.number)
            : "";

    this.channelName.textContent =
        channel.name ?? "";

    this.updateLogo(channel);

    this.title.textContent =
        channel.event ?? "Keine Programminformation";

    this.progressFill.style.width =
        `${this.calculateProgress(channel)}%`;

    this.start.textContent =
        this.formatTime(channel.start);

    this.stop.textContent =
        this.formatTime(channel.stop);

    this.root.classList.remove("hidden");

    if (this.hideTimer !== null) {
        window.clearTimeout(this.hideTimer);
    }

    this.hideTimer = window.setTimeout(
        () => this.hide(),
        duration
    );
}

    hide() {
        if (!this.root) {
            return;
        }

        this.root.classList.add("hidden");
    }

    formatTime(timestamp) {
        if (!timestamp) {
            return "--:--";
        }

        return new Date(timestamp * 1000).toLocaleTimeString(
            "de-CH",
            {
                hour: "2-digit",
                minute: "2-digit",
            }
        );
    }

    clampProgress(value) {
        const progress = Number(value);

        if (!Number.isFinite(progress)) {
            return 0;
        }

        return Math.max(0, Math.min(100, progress));
    }

    updateLogo(channel) {
        if (!this.logo) {
            return;
        }

        const logoUrl = channel?.logo?.trim();

        if (!logoUrl) {
            this.logo.hidden = true;
            this.logo.removeAttribute("src");
            this.logo.alt = "";
            return;
        }

        this.logo.src = logoUrl;
        this.logo.alt = channel.name
            ? `Logo von ${channel.name}`
            : "Senderlogo";

        this.logo.hidden = false;
    }
    calculateProgress(channel) {
        const start = Number(channel?.start);
        const stop = Number(channel?.stop);
        const now = Math.floor(Date.now() / 1000);

        if (
            !Number.isFinite(start) ||
            !Number.isFinite(stop) ||
            stop <= start
        ) {
            return this.clampProgress(channel?.progress);
        }

        const progress =
            ((now - start) / (stop - start)) * 100;

        return this.clampProgress(progress);
    }
async toggleFullscreen() {
    try {
        if (!document.fullscreenElement) {
            await document.documentElement.requestFullscreen();
        } else {
            await document.exitFullscreen();
        }
    } catch (error) {
        console.error(
            "Fullscreen konnte nicht umgeschaltet werden:",
            error
        );
    }
}

}
