def align_matches(self, matches: List[Tuple[int, int]], dedup_hashes: Dict[str, int], queried_hashes: int,
                  topn: int = TOPN) -> List[Dict[str, any]]:
    """
    Finds hash matches that align in time with other matches and finds
    consensus about which hashes are "true" signal from the audio.

    :param matches: matches from the database
    :param dedup_hashes: dictionary containing the hashes matched without duplicates for each song
    (key is the song id).
    :param queried_hashes: amount of hashes sent for matching against the db
    :param topn: number of results being returned back.
    :return: a list of dictionaries (based on topn) with match information.
    """
    # count offset occurrences per song and keep only the maximum ones.
    sorted_matches = sorted(matches, key=lambda m: (m[0], m[1]))
    counts = [(*key, len(list(group))) for key, group in groupby(sorted_matches, key=lambda m: (m[0], m[1]))]
    songs_matches = sorted(
        [max(list(group), key=lambda g: g[2]) for key, group in groupby(counts, key=lambda count: count[0])],
        key=lambda count: count[2], reverse=True
    )

    songs_result = []
    for song_id, offset, _ in songs_matches[0:topn]:  # consider topn elements in the result
        song = self.db.get_song_by_id(song_id)

        song_name = song.get(SONG_NAME, None)
        song_hashes = song.get(FIELD_TOTAL_HASHES, None)
        nseconds = round(float(offset) / DEFAULT_FS * DEFAULT_WINDOW_SIZE * DEFAULT_OVERLAP_RATIO, 5)
        hashes_matched = dedup_hashes[song_id]

        song = {
            SONG_ID: song_id,
            SONG_NAME: song_name.encode("utf8"),
            INPUT_HASHES: queried_hashes,
            FINGERPRINTED_HASHES: song_hashes,
            HASHES_MATCHED: hashes_matched,
            # Percentage regarding hashes matched vs hashes from the input.
            INPUT_CONFIDENCE: round(hashes_matched / queried_hashes, 2),
            # Percentage regarding hashes matched vs hashes fingerprinted in the db.
            FINGERPRINTED_CONFIDENCE: round(hashes_matched / song_hashes, 2),
            OFFSET: offset,
            OFFSET_SECS: nseconds,
            FIELD_FILE_SHA1: song.get(FIELD_FILE_SHA1, None).encode("utf8")
        }

        songs_result.append(song)

    return songs_result

def return_matches(self, hashes: List[Tuple[str, int]],
                       batch_size: int = 1000) -> Tuple[List[Tuple[int, int]], Dict[int, int]]:
        """
        Searches the database for pairs of (hash, offset) values.

        :param hashes: A sequence of tuples in the format (hash, offset)
            - hash: Part of a sha1 hash, in hexadecimal format
            - offset: Offset this hash was created from/at.
        :param batch_size: number of query's batches.
        :return: a list of (sid, offset_difference) tuples and a
        dictionary with the amount of hashes matched (not considering
        duplicated hashes) in each song.
            - song id: Song identifier
            - offset_difference: (database_offset - sampled_offset)
        """
        # Create a dictionary of hash => offset pairs for later lookups
        mapper = {}
        for hsh, offset in hashes:
            if hsh.upper() in mapper.keys():
                mapper[hsh.upper()].append(offset)
            else:
                mapper[hsh.upper()] = [offset]

        values = list(mapper.keys())

        # in order to count each hash only once per db offset we use the dic below
        dedup_hashes = {}

        results = []
        with self.cursor() as cur:
            for index in range(0, len(values), batch_size):
                # Create our IN part of the query
                query = self.SELECT_MULTIPLE % ', '.join([self.IN_MATCH] * len(values[index: index + batch_size]))

                cur.execute(query, values[index: index + batch_size])

                for hsh, sid, offset in cur:
                    if sid not in dedup_hashes.keys():
                        dedup_hashes[sid] = 1
                    else:
                        dedup_hashes[sid] += 1
                    #  we now evaluate all offset for each  hash matched
                    for song_sampled_offset in mapper[hsh]:
                        results.append((sid, offset - song_sampled_offset))

            return results, dedup_hashes
