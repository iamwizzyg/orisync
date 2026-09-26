# Orisync

A production-grade supply chain event tracking API with webhook delivery,
role-based access control, observability, and CI/CD.

**Live API:** https://orisync-production.up.railway.app  
**API Docs:** https://orisync-production.up.railway.app/docs  
**Health:** https://orisync-production.up.railway.app/health

![CI](https://github.com/iamwizzyg/orisync/actions/workflows/ci.yml/badge.svg)

---

## The Problem

Small manufacturers and logistics teams track supplier deliveries, inventory
movements, and purchase orders manually or through spreadsheets. When a
shipment is delayed or an anomaly occurs, they find out late. Orisync provides
a backend system that ingests supply chain events, stores them with full audit
history, fires webhook notifications to external systems on state changes, and
exposes a clean REST API for querying.

---

## What I Built

A REST API that:

- Accepts supply chain events (ORDERED, SHIPPED, DELAYED, RECEIVED, ANOMALY)
  from any internal or external system
- Stores events permanently with idempotency protection against duplicate
  submissions
- Fires webhook notifications to registered endpoints when events match
  subscription rules
- Retries failed webhook deliveries with exponential backoff
- Signs webhook payloads with HMAC-SHA256 so receivers can verify authenticity
- Enforces role-based access control across three roles: ADMIN, OPERATOR, VIEWER
- Exposes Prometheus metrics for API throughput, event volumes, and webhook
  delivery rates
- Deploys to cloud with automated database migrations on every release

---

## Architecture

