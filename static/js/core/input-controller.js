import {
    navigationController
} from "./navigation-controller.js";

class InputController {
    constructor() {
        this.started = false;
        this.touchStartX = 0;
        this.touchStartY = 0

        this.handleKeyDown =
            this.handleKeyDown.bind(this);
        this.handleTouchStart = this.handleTouchStart.bind(this);
        this.handleTouchEnd = this.handleTouchEnd.bind(this);    
    }

    start() {
        if (this.started) {
            return;
        }

        document.addEventListener(
            "keydown",
            this.handleKeyDown
        );

        document.addEventListener(
            "touchstart",
            this.handleTouchStart,
            { passive: true }
        );

        document.addEventListener(
            "touchend",
            this.handleTouchEnd,
            { passive: true }
        );

        this.started = true;
    }

    stop() {
        if (!this.started) {
            return;
        }

        document.removeEventListener(
            "keydown",
            this.handleKeyDown
        );

        document.removeEventListener(
            "touchstart",
            this.handleTouchStart,
            { passive: true }
        );

        document.removeEventListener(
            "touchend",
            this.handleTouchEnd,
            { passive: true }
        );

        this.started = false;
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

        if (
            Math.abs(deltaX) < threshold &&
            Math.abs(deltaY) < threshold
        ) {
            return;
        }

        if (Math.abs(deltaX) > Math.abs(deltaY)) {
            if (deltaX > 0) {
                navigationController.moveRight();
            } else {
                navigationController.moveLeft();
            }

            return;
        }

        if (deltaY > 0) {
            navigationController.moveUp();
        } else {
            navigationController.moveDown();
        }
    }   

    handleKeyDown(event) {
        if (this.isEditableTarget(event.target)) {
            return;
        }
        const action = this.resolveAction(event);

        if (!action) {
            return;
        }

        event.preventDefault();
        event.stopPropagation();

        action();
    }

    isEditableTarget(target) {
    if (!(target instanceof HTMLElement)) {
        return false;
    }

    return (
        target.matches(
            "input, textarea, select"
        ) ||
        target.isContentEditable
      );
    }

    resolveAction(event) {
        switch (event.key) {
            case "ArrowUp":
                return () =>
                    navigationController.moveUp();

            case "ArrowDown":
                return () =>
                    navigationController.moveDown();

            case "ArrowLeft":
                return () =>
                    navigationController.moveLeft();

            case "ArrowRight":
                return () =>
                    navigationController.moveRight();

            case "Enter":
            case " ":
                return () =>
                    navigationController.activate();

            case "Escape":
            case "Backspace":
                return () =>
                    navigationController.back();

            default:
                return null;
        }
    }
}

export const inputController =
    new InputController();