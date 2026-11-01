const priceFormatter = new Intl.NumberFormat("da-DK", { maximumFractionDigits: 0 });

const dateTimeFormatter = new Intl.DateTimeFormat("da-DK", {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
});

const dateFormatter = new Intl.DateTimeFormat("da-DK", {
    day: "numeric",
    month: "short",
    year: "numeric",
});

export function formatPrice(price: number): string {
    return `${priceFormatter.format(price)} kr.`;
}

/** Shows a timestamp in the viewer's local time, for example "31. okt. 2026 10.30". */
export function formatDateTime(iso: string): string {
    return dateTimeFormatter.format(new Date(iso));
}

export function formatDate(iso: string): string {
    return dateFormatter.format(new Date(iso));
}

export function formatAge(hours: number): string {
    if (hours < 1) {
        return "under en time gammel";
    }

    if (hours < 48) {
        return `${Math.round(hours)} timer gammel`;
    }

    return `${Math.round(hours / 24)} dage gammel`;
}
