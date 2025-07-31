# LLM generates rich text + keywords + hard constraints from the query (stored as JSON?)


# The LLM output is embedded in the same space as the media VDB


# This vector is used to get the "top K" closest media, taking hard constraints into account (payload filtering)


# The top K are re-ranked [find a way]


# The selected media in the top K are queried from the media DB and returned