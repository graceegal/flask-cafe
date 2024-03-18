"use strict";

/** ProcessLike: handles liking and unliking a cafe via button
 *
 * - Make API call to server to check if cafe is liked by curr user or not
 * - if user likes cafe, update button to have unlike option and update DB
 * - else if user unlikes a cafe, change button to have like option and update DB
 */
async function processLike(evt) {
  evt.preventDefault();

  debugger;
  const cafeId = $("#like-form").attr("cafe-id");

  const resp = await fetch(`/api/likes?cafe_id=${cafeId}`);
  const likedData = await resp.json();
  const liked = likedData.likes;

  if (liked) {
    await unlikeCafe(cafeId);
  } else {
    await likeCafe(cafeId);
  }
}

/** likeCafe: updates UI to show "Unlike" & updates DB */
async function likeCafe(cafeId) {
  $("#like-btn").text("Liked");

  const resp = await fetch(
    '/api/like',
    {
      method: "POST",
      body: JSON.stringify({ cafe_id: cafeId }),
      headers: { "Content-Type": "application/json" }
    });

  const data = await resp.json();

  console.log(data);
}

/** unlikeCafe: updates UI to show "Like" & updates DB */
async function unlikeCafe(cafeId) {
  $("#like-btn").text("Like");

  const resp = await fetch(
    '/api/unlike',
    {
      method: "POST",
      body: JSON.stringify({ cafe_id: cafeId }),
      headers: { "Content-Type": "application/json" }
    });

  const data = await resp.json();

  console.log(data);
}


$("#like-form").on("submit", processLike);