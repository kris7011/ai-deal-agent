import { formatAge, formatDateTime } from "../format";
import type { Freshness } from "../types";

type DataSourceNoticeProps = {
    dataSource: Freshness;
};

function DataSourceNotice({ dataSource }: DataSourceNoticeProps) {
    return (
        <div className={`data-source data-source-${dataSource.origin}`} role="status">
            <strong>{dataSource.origin_label}</strong>
            <span>
                Hentet fra kilden {formatDateTime(dataSource.fetched_at)} ({formatAge(dataSource.age_hours)})
            </span>
            <span className={`freshness-badge freshness-${dataSource.status}`}>{dataSource.status_label}</span>
            {dataSource.origin === "demo" && (
                <p className="data-source-note">
                    Produkterne, butikkerne og priserne er opfundet til demonstration. Det er ikke rigtige tilbud.
                </p>
            )}
        </div>
    );
}

export default DataSourceNotice;
