Canvas CLI tool for Norwegian LMS instances.
Install: ln -sf ~/projects/study-workbench/scripts/canvas ~/.local/bin/canvas

Usage:
    canvas courses          List active courses
    canvas assignments      List all assignments sorted by due date
    canvas files            List downloadable files per course
    canvas download         Download all course files to curriculum/
    canvas syllabus         Export syllabus/assignment ledger to xlsx
    canvas calendar         Upcoming deadlines (next 14 days)
    canvas grades           Show grades per course
    canvas announce         Recent announcements

Flags: --skip ID,ID  --only ID,ID  --no-pages
Requires: canvasapi, openpyxl (pip install --break-system-packages)
Source: ~/projects/study-workbench/scripts/canvas