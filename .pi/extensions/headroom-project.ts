// Keep Pi compression/retrieval on this project's proxy, not the global endpoint.
export default function () {
  process.env.HEADROOM_BASE_URL = "http://127.0.0.1:8791";
}
