# Capitalising the pronouns for God in a lecture edition (brief for the agents)

Used for the Kapila Gītā booklets (2026-10-23): `pronoun_tags.py tag` writes `kgNN_tagged.md` and `kgNN_tags.json`; an agent per two or three lectures answers in `kgNN_caps.json`; `pronoun_tags.py apply` capitalises and checks that only the case of the listed words changed. Adapt the names of the lecture series below for another series.

The Kapila Gītā lectures of Gosvāmī Śrī Śyām Manoharjī (English discourses on Śrīmad Bhāgavata 3.25–33, Kapila's teaching to his mother Devahūti) are being set as booklets in the house style of the owner's English publications. That style capitalises the pronouns for God: **He, His, Him, Himself**, and **You, Your, Yours, Yourself** when God is addressed. Your task is to decide, for every tagged pronoun in your lectures, whether it refers to God.

## Files

- `kgNN_tagged.md` in this folder: the lecture, in pandoc markdown. Every lowercase *he, his, him, himself* outside italics carries a tag such as `he⟦h12⟧`; every lowercase *you, your, yours, yourself* in a paragraph that names God carries a tag such as `you⟦y7⟧`. Italic spans (`*…*`) are Sanskrit, Hindi or Gujarati and are not tagged.
- Write your answer for each lecture to `kgNN_caps.json` in this folder. Do not change any other file.

## How to decide

Read the whole lecture in order before answering (in chunks if needed): the referent of a pronoun is often set up several sentences or paragraphs earlier, and the speaker moves quickly between Bhagavān, sages, devotees, his students and hypothetical persons.

Capitalise (list the id) when the pronoun refers to **God, Bhagavān, in any of His forms**:

- Bhagavān, the Lord, God, Śrī Kṛṣṇa, Viṣṇu, Nārāyaṇa, Hari, Rāma, Narasiṃha and the other avatāras when spoken of as Bhagavān; Ṭhākurjī; Puruṣottama.
- **Kapila**, the teacher of the Kapila Gītā, Devahūti's son, Bhagavān's avatāra. If the speaker clearly distinguishes another Kapila (for example the founder of an atheistic Sāṅkhya whom he treats as a different person), follow his distinction and leave that one lowercase.
- Vāsudeva, Saṅkarṣaṇa, Pradyumna, Aniruddha when spoken of as forms of Bhagavān presiding over citta, ahaṅkāra, buddhi, manas.
- Paramātmā, Antaryāmī, Īśvara, the Supreme Puruṣa, Brahman when spoken of as a person ("he"), when they mean God.
- **You / Your / Yourself** when someone addresses God: a devotee's prayer (Kuntī to Kṛṣṇa, Devahūti to Kapila, Nalakūbara to Kṛṣṇa), a verse rendered in English, or the speaker himself addressing the Lord.

Leave lowercase (do not list):

- the speaker, his students and listeners, and "you" addressed to them (most of the you-tags);
- God speaking to a devotee ("I will give you": *you* is the devotee);
- sages, gods and devotees: Vyāsa, Nārada, Brahmā, Śiva, Indra and the devas, Kardama, Manu, Śukadeva, Parīkṣit, Uddhava, Prahlāda, Dhruva, the gopīs; Devahūti is "she";
- the ācāryas and teachers: Mahāprabhuji (Vallabhācārya), Gosāīṃjī, Śaṅkarācārya, Rāmānuja, Madhva, a guru;
- the jīva, the ātmā or puruṣa as the individual self, a bhakta, a sādhaka, a king, an asura, an example person ("if somebody does this, he will …"), a scientist, a philosopher;
- Kāla, prakṛti, mahat and the other tattvas unless the sentence plainly speaks of them as Bhagavān Himself.

**When in doubt, leave it lowercase** and list it under `doubtful` with a few words of reason. A missed capital is a small blemish; a wrong one ("He" for Vyāsa) misstates the doctrine.

## Output

One JSON file per lecture, exactly in this shape (ids only from that lecture's tags):

```json
{
  "lecture": "01",
  "capitalise": [
    {"id": "h12", "referent": "Kṛṣṇa"},
    {"id": "y7", "referent": "Kṛṣṇa (Kuntī's prayer)"}
  ],
  "doubtful": [
    {"id": "h40", "note": "could be Vyāsa or Kṛṣṇa"}
  ]
}
```

Before you finish, check that every id you list exists in the tagged file, that no id is listed twice, and that the JSON parses (`python3 -c "import json;json.load(open('kgNN_caps.json'))"`). Your final reply: one short paragraph per lecture with the number of capitalised he-forms and you-forms and anything you were unsure about.
