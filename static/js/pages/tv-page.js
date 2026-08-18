import { Page } from "../core/page.js";
import { eventBus } from "../core/event-bus.js";
import { Events } from "../core/events.js";
import { ChannelList } from "../widgets/channel-list.js";
import { Player } from "../widgets/player.js";
import { ChannelInfo } from "../widgets/channel-info.js";
import { OSD } from "../widgets/osd.js";
import {
    navigationController
} from "../core/navigation-controller.js";


export class TVPage extends Page {
    constructor() {
        super();

        this.channelList = null;
        this.player = null;
        this.osd = null;
        this.channelInfo = null;
        this.currentChannel = null;
        this.unsubscribers = [];
        this.touchStartX = 0;
        this.touchStartY = 0;

        this.handleTouchStart =
            this.handleTouchStart.bind(this);

        this.handleTouchEnd =
            this.handleTouchEnd.bind(this);
        this.handleChannelChange =
            this.handleChannelChange.bind(this);

        this.handleChannelActivate =
            this.handleChannelActivate.bind(this);

        this.handleChannelClose =
            this.handleChannelClose.bind(this);

        this.handleDetailsOpen =
            this.handleDetailsOpen.bind(this);
    }

    initialize() {
        if (!document.querySelector("#channel-list")) {
            return;
        }

        this.unsubscribers.push(
            eventBus.on(
                Events.CHANNEL_CHANGE,
                (channel) => this.handleChannelChange(channel)
            )
        );

        this.unsubscribers.push(
            eventBus.on(
                Events.CHANNEL_ACTIVATE,
                (channel) => this.handleChannelActivate(channel)
            )
        );

        this.unsubscribers.push(
            eventBus.on(
                Events.CHANNEL_LIST_CLOSE,
                () => this.handleChannelClose()
            )
        );

        this.unsubscribers.push(
            eventBus.on(
                Events.CHANNEL_DETAILS_OPEN,
                (channel) => this.handleDetailsOpen(channel)
            )
        );

        this.root = document.querySelector("#tv");

        this.root?.addEventListener(
            "touchstart",
            this.handleTouchStart,
            { passive: true }
        );

        this.root?.addEventListener(
            "touchend",
            this.handleTouchEnd,
            { passive: true }
        );

        this.channelList = new ChannelList("#channel-list");
        this.channelList.initialize();

        this.player = new Player("#tv-player");
        this.player.initialize();

        this.osd = new OSD("#osd");
        this.osd.initialize();

        this.channelInfo = new ChannelInfo("#channel-info");
        this.channelInfo.initialize();

        this.activatePendingChannel();
        navigationController.setTarget(this);
    }



    destroy() {
        for (const unsubscribe of this.unsubscribers) {
            unsubscribe();
        }

        this.unsubscribers = [];
        this.channelInfo?.destroy();
        this.player?.destroy();
        this.channelList?.destroy();
        this.osd?.destroy();
        navigationController.clearTarget(this);
        this.root?.removeEventListener(
            "touchstart",
            this.handleTouchStart
        );

        this.root?.removeEventListener(
            "touchend",
            this.handleTouchEnd
        );
    }

    handleTouchStart(event) {
        const touch = event.changedTouches[0];

        this.touchStartX = touch.clientX;
        this.touchStartY = touch.clientY;
    }

    handleTouchEnd(event) {
        const touch = event.changedTouches[0];

        const deltaX =
            touch.clientX - this.touchStartX;

        const deltaY =
            touch.clientY - this.touchStartY;

        const threshold = 40;

        // kein Swipe -> hier nichts machen
        if (
            Math.abs(deltaX) < threshold &&
            Math.abs(deltaY) < threshold
        ) {
            return;
        }

        // horizontal
        if (Math.abs(deltaX) > Math.abs(deltaY)) {
            if (deltaX > 0) {
                eventBus.emit(
                    Events.CHANNEL_LIST_SHOW
                );
            }

            return;
        }

        // vertikal nur bei sichtbarer Senderliste
        if (!this.channelList?.isVisible()) {
            return;
        }

        if (deltaY < 0) {
            navigationController.moveDown();
        } else {
            navigationController.moveUp();
        }
    }

    handleVideoClick() {
        if (!this.currentChannel) {
            return;
        }

        eventBus.emit(
            Events.OSD_SHOW,
            this.currentChannel
        );
    }

    handleChannelChange(channel) {
        console.log(channel);
    }

    handleChannelActivate(channel) {
        this.currentChannel = channel;
        console.log("Sender ausgewählt:", channel);
    }

    handleDetailsOpen(channel) {
        console.log(channel);
    }

    handleChannelClose() {
        window.location.href = "/";
    }
    activatePendingChannel() {
        const storageKey = "tvh-quick-gui.pending-channel";
        const storedChannel = sessionStorage.getItem(storageKey);

        if (!storedChannel) {
            return;
        }

        sessionStorage.removeItem(storageKey);

        try {
            const channel = JSON.parse(storedChannel);

            if (!channel?.uuid || !channel?.streamUrl) {
                return;
            }

            this.channelList?.selectByUuid(channel.uuid, {
                animate: false,
                focus: false,
            });

            this.currentChannel = channel;

            eventBus.emit(
                Events.CHANNEL_ACTIVATE,
                channel
            );

            eventBus.emit(
                Events.CHANNEL_LIST_HIDE
            );
        } catch (error) {
            console.error(
                "Gespeicherter Guide-Sender ist ungültig:",
                error
            );
        }
    }

    back() {
        window.location.assign("/");
    }

    moveLeft() {
        const infoPanel = document.querySelector("#channel-info");
        const channelList = document.querySelector("#channel-list");

        const infoVisible =
            infoPanel &&
            !infoPanel.classList.contains("hidden");

        const channelListVisible =
            channelList &&
            !channelList.classList.contains("hidden");

        if (infoVisible) {
            eventBus.emit(Events.CHANNEL_DETAILS_CLOSE);
            return;
        }

        if (channelListVisible) {
            eventBus.emit(Events.CHANNEL_LIST_HIDE);
            return;
        }

        eventBus.emit(Events.CHANNEL_LIST_SHOW);
    }
    moveRight() {
        const channel = this.channelList?.getSelectedChannel();

        if (!channel) {
            return;
        }

        eventBus.emit(
            Events.CHANNEL_DETAILS_OPEN,
            channel
        );

        eventBus.emit(Events.CHANNEL_LIST_HIDE);
    }

    moveUp() {
        console.log(
            "ChannelList sichtbar:",
            this.channelList?.isVisible()
        )
        if (this.channelList?.isVisible()) {
            this.channelList.selectPrevious();
            return;
        }

        if (!this.currentChannel) {
            return;
        }

        eventBus.emit(Events.OSD_SHOW, {
            channel: this.currentChannel,
            duration: 8000,
        });
    }

    moveDown() {
        if (this.channelList?.isVisible()) {
            this.channelList.selectNext();
            return;
        }

        // später direktes Zapping
    }

    activate() {
        if (!this.channelList?.isVisible()) {
            return;
        }

        this.channelList.activateSelected();
    }

}
