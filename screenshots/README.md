# Application screenshots

Use the redesigned desktop interface to capture real demo runs. No screenshots have been added yet.

## Open the updated app

Download a fresh ZIP from GitHub and extract it. Open Terminal in the new project folder, then run:

```bash
python3 reloop.py gui
```

Close an older running window first. Preserve your old local_state.json if you need its demo history; downloading a fresh folder otherwise starts a fresh demo.

## Recommended screenshots

1. **matching.png** — In **Find resources**, select **Demo Community School (School)**, enter `display for computer lab`, quantity `2`, radius `10`, and click **Find matches**. Capture the resource cards.
2. **transfer.png** — Click **Review transfer** on a monitor card. Enter quantity `2`, a demo purchase benchmark of `6000`, transport `300`, and refurbishment `250`. Capture the form. Tick the inspection checkbox only as part of this fictional demo, then click **Confirm demo transfer**.
3. **impact.png** — The app opens **Reuse impact** after confirmation. Capture the metric cards and recorded transfer.
4. **partners.png** — Open **Partner network** to capture the fictional institutions and approval states.

These are synthetic examples, not real donations. Keep the demo disclosure visible.

On macOS, press **Shift + Command + 4** and select the application window area. Crop out unrelated personal information.

## Add to GitHub

Open this folder and use **Add file → Upload files**, then commit your PNG files. To display existing captures in the root README, add:

```markdown
![Resource matching](screenshots/matching.png)
![Transfer review](screenshots/transfer.png)
![Reuse impact](screenshots/impact.png)
![Partner network](screenshots/partners.png)
```

Only add image links after their files exist. You can also send your screenshots in the chat to have them uploaded.
