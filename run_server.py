#!/usr/bin/env python
# -*- coding: utf-8 -*-

import uvicorn

if __name__ == "__main__":
    uvicorn.run("ansible_events_ui.app:app", host="0.0.0.0", port=8080, log_level="info")
