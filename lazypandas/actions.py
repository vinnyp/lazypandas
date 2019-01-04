import logging

logger = logging.getLogger(__name__)


def split_and_fill(df, source, target, separator):
    map_null_cells = (df[target].isnull())
    map_content_cells = (df[source].notnull())

    # Find all cells that have an empty target and content in the source.
    # Store the list in a copy so we can reference it later.
    df_backfill = df.loc[map_null_cells & map_content_cells]
    records = len(df.loc[map_null_cells & map_content_cells])
    logger.debug("Records to backfill: %s", str(records))

    # Backfill the target cell with a split from source by separator
    df.loc[map_null_cells & map_content_cells, target] = \
        (df.loc[map_null_cells & map_content_cells, source].apply(lambda x: x.split(separator)[1]))

    df.loc[df_backfill.index, source] = \
        df.loc[df_backfill.index, source].apply(lambda x: x.split(separator)[0])

    remaining_records = len(df.loc[map_null_cells & map_content_cells])
    logger.debug("Remaining records to backfill: %s", str(remaining_records - records))

    return df
