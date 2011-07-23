import re

def Start():
  HTTP.CacheTime = CACHE_1WEEK
  HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_5; en-us) AppleWebKit/533.19.4 (KHTML, like Gecko) Version/5.0.3 Safari/533.19.4'
  HTTP.Headers['Referer'] = 'http://www.imdb.com/'

class UnofficialImdbApi(Agent.Movies):
  name = '*Unofficial IMDb API'
  languages = [Locale.Language.English]
  primary_provider = False
  contributes_to = ['com.plexapp.agents.imdb']

  def search(self, results, media, lang):
    imdbid = media.primary_metadata.id
    results.Append(MetadataSearchResult(id=imdbid, score=99))

  def update(self, metadata, media, lang):
    url = 'http://www.imdbapi.com/?i=%s&plot=full&tomatoes=true' % metadata.id

    try:
      movie = JSON.ObjectFromURL(url, sleep=2.0)
    except:
      Log('Failed when trying to open url: ' + url)
      movie = None

    if movie is not None:
      if movie['Response'] == 'True':
        metadata.title = movie['Title']
        metadata.year = int(movie['Year'])
        metadata.content_rating = movie['Rated']
        metadata.originally_available_at = Datetime.ParseDate(movie['Released']).date()

        metadata.genres.clear()
        kids = ['Animation','Family']
        for genre in movie['Genre'].split(','):
          metadata.genres.add(genre.strip())
          if genre.strip() in kids:
            metadata.collections.add("Kid's Movies")

        metadata.writers.clear()
        for writer in movie['Writer'].split(','):
          metadata.writers.add(writer.strip())

        metadata.directors.clear()
        for director in movie['Director'].split(','):
          metadata.directors.add(director.strip())

        metadata.roles.clear()
        for actor in movie['Actors'].split(','):
          role = metadata.roles.new()
          role.actor = actor.strip()

        metadata.summary = movie['Plot']
        
        metadata.rating = float(movie['Rating'])
        
        if Prefs['collection']:
          if movie['tomatoImage'] == 'certified':
            metadata.collections.add("Rotten Tomatoes 'Certified Fresh'")
        
        if Prefs['tomatoes']:
          if int(movie['tomatoReviews']) > int(Prefs['tomatoes_reviews']):
            metadata.rating = float(movie['tomatoMeter']) / 10

        duration = 0
        try:
          runtime = re.search('([0-9]+) hrs? ([0-9]+) min', movie['Runtime'])
          duration += int(runtime.group(1)) * 60 * 60 * 1000
          duration += int(runtime.group(2)) * 60 * 1000
        except:
          pass
        if duration > 0:
          metadata.duration = duration

        if Prefs['imdb_poster']:
          try:
            poster = movie['Poster']
            fullsize = poster.split('@@')[0] + '@@._V1._SX640.jpg'
            thumb    = poster.split('@@')[0] + '@@._V1._SX100.jpg'
            if fullsize not in metadata.posters:
              p = HTTP.Request(thumb)
              metadata.posters[fullsize] = Proxy.Preview(p, sort_order=1)
          except:
            pass
        else:
          try:
            poster = movie['Poster']
            del metadata.posters[poster]
          except:
            pass

      else:
        Log('An error occured. The json response is:')
        Log(movie)
