import {
    navigationController
} from "./navigation-controller.js";

class InputController {
    constructor() {
        this.started = false;

        this.handleKeyDown =
            this.handleKeyDown.bind(this);
    }

    start() {
        if (this.started) {
            return;
        }

        document.addEventListener(
            "keydown",
            this.handleKeyDown
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

        this.started = false;
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