# Spotify Analytics Dashboard

Hello! This is small and simple project to allow you to look at your extened Spotify streaming history.

## Why make this?

Spotify wrapped is great (if not a bit dissapointing at times), but it only shows you a summary of you listening history for the past year (not including December). There are other apps and websites out there that can provide you a look at your listening history, but due to a change in how Spotify shares listening history, they can no longer provide analytics on your whole listening history.

Here, GDPR comes to the rescue. Under GDPR laws, you can request your 'Extended Streaming History' from [Spotify](https://www.spotify.com/uk/account/privacy/), and it is provided to you for free. With this in mind, I decided to start to build the dashboard, with it being a great excuse to learn [Streamlit](https://streamlit.io/) and brush up on my [pandas](https://pandas.pydata.org/).

## How do I use this it?!

Unlike other analytic platforms, this dashboard does not connect to your Spotify account, to use it you will **need** a copy of your 'Extended Streaming History' from Spotify, you can request it [here](https://www.spotify.com/uk/account/privacy/). Then simply upload all files with names like Streaming_History_Audio_2018-2019_0.json. Once you have uploaded your data, you will be able to download your data as a .parquet files for faster uploads and inital reading, at the expense of human readabilty.

---
Hope you find it fun and possibly find some insightful statistics!
