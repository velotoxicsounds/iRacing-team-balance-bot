from datetime import datetime as dt
import discord
import re
from textwrap import dedent

MESSAGE_TEXT_RE = re.compile(r'<@!*\d+> (.*)')
TEAM_SEPARATOR = ';'
DRIVER_SEPARATOR = ','

class DiscordChannel:
  
  def __init__(self, client):
    self.bot = None
    self.channel = None
    self.client = client
    self.message = None
  
  async def indicate_progress(self):
    await self.channel.trigger_typing() 
  
  def is_monitoring_possible(self):
    channel_id = self.bot.get_monitoring_data().get('channel_id')
    return channel_id is not None
  
  async def list_commands(self):
    commands_list_part_1 = dedent('''
      List of commands:
      
      **status** - zeigt den aktuellen Status der Serverdaten und die Aktionen an, die ich mit diesen Daten ausführen kann.
      
      **drivers** - Liste der hinzugefügten Treiber für diesen Server anzeigen
      **add driver** Driver-ID *DRIVER-ID* - Fügen Sie diesen Fahrer der Fahrerliste für diesen Server hinzu.
          Sie können mehrere Fahrer durch Kommas trennen.
          Sie können nur den Fahrernamen schreiben, und ich werde die Driver-ID für Sie suchen.
          Ich werde regelmäßig das iRating jedes Fahrers überprüfen und es zwischenspeichern, wenn es geändert wurde.
      **remove driver** Driver Name - Entfernen Sie diesen Fahrer aus der Fahrerliste für diesen Server.
      **clear drivers** - Löschen Sie die Fahrerliste für diesen Server.
          Ich werde nichts überwachen oder Sie überhaupt warnen, wenn Sie keine Fahrer haben, also ist dies eine gute Möglichkeit, mich zwischen den Ereignissen wissen zu lassen, dass ich nichts tun muss.
      
      **recheck rating** Driver Name - manuell eine erneute Überprüfung des benannten Fahrers und dessen iRating auslösen.
      **recheck rating all** - manuell eine Erneute Überprüfung aller Fahrer-iRatings auslösen.
    
      **team sizes** - zeigt die zulässigen Teamgrößen für das aktuelle Ereignis an. Ich werde nur Teams dieser Größe bei der Berechnung der Balance zulassen.
          Sobald Teamgrößen festgelegt sind (und Fahrer hinzugefügt werden), werde ich über die optimale Balance berichten, wenn diese sich ändert.
      **set team sizes** *m*, *n*, ... - legen Sie die zulässigen Teamgrößen für das aktuelle Ereignis fest. Ich lasse nur Teams dieser Größen bei der Berechnung der Bilanz zu.
    ''').strip()
    await self.print(commands_list_part_1)
    commands_list_part_2 = dedent('''
      **combine drivers** Driver Name, Driver Name, .... - Kraftbilanzberechnungen, um nur Gruppen von Teams zu berücksichtigen, bei denen die benannten Fahrer in einem Team zusammen sind.
        Beachten Sie, dass die Verwendung dieser Funktion die Fähigkeit Ihres Servers, die Fahrer auszugleichen, erheblich beeinträchtigen kann.
      **combinations** - aktuelle Kombinationen von Fahrern anzeigen.
      **remove combination** Driver Name, Driver Name, ... - entfernen Sie die Kombination der aufgeführten Fahrer.
      **clear combinations** - alle Kombinationen löschen.
    ''').strip().format(self.client.user)
    await self.print(commands_list_part_2)
    commands_list_part_3 = dedent('''
      **balance** - zuletzt berechnete optimale Balance der Teammitglieder in Teams.
      **recalculate balance** - manuell eine erneute Überprüfung der optimalen Balance basierend auf den zuletzt zwischengespeicherten Fahrer-iRatings auslösen.
      
      **teams** - feste Teams für die kommende Veranstaltung anzuzeigen.
          Ich werde die Bilanz dieser Teams überwachen, um sicherzustellen, dass sie nicht außerhalb des konfigurierten Schwellenwerts liegt. 
      **set teams** Driver Name, Driver Name, ...; ... - feste Teams für das kommende Event festlegen. Teammitglieder sind durch Kommas getrennt, und Teams sind semikolonngetrennt.
      **set teams according to balance** setzt die Teams auf die zuletzt berechnete optimale Balance.
      **clear teams** - die festen Teams für die kommende Veranstaltung zu löschen.
      
      **balance threshold** - den Saldoschwellenwert anzeigen.
          Wenn die Lücke zwischen dem durchschnittlichen IRating der teams außerhalb dieses Schwellenwerts liegt, werde ich Sie benachrichtigen.
          Bevor feste Teams festgelegt werden, werde ich auch feststellen, wenn die aktuelle optimale Balance außerhalb dieser Schwelle liegt - aber ich würde mir noch keine allzu großen Sorgen machen.
      **set balance threshold** *n* - den Saldoschwellenwert festlegen.
      
      **set notification channel** - legen Sie diesen Discord-Kanal als den Kanal fest, den ich zum Senden von Benachrichtigungen verwenden sollte.
      **notification channel** - Überprüfen, welcher Kanal für Benachrichtigungen konfiguriert wurde
      
      Denken Sie daran, mich am Anfang einer Befehlsnachricht mit {0.mention} zu makieren !
    ''').strip().format(self.client.user)
    await self.print(commands_list_part_3)
    commands_list_part_4 = dedent('''
    List of commands:
    
    
    **ZWEITER BOT** - Eigen Produktion Team Happen:
	**FÜR DIESE BEFEHLE BRAUCHST DU DEN BOT NICHT MAKIEREN, HIER REICHT !happen_DEINBEFEHL**


    **!happen_saveid <DeineIRACINGID>**
        - [Hier zu finden https://members.iracing.com/membersite/account/Home.do , auf der rechten Seite über dem Menü Customer ID: XXXXXX] Dient zur automatischen Registrierung
    
        
    **ADMIN UND MODIS**
      
    **!happen_allseries**
        - Dadurch wird eine Liste aller aktuellen aktiven Seriennamen und IDs angezeigt (die für die bevorzugten Serienbefehle verwendet werden).
    **!happen_setfavseries <Series IDs>** 
        - Dadurch wird die Favoritenserie für Ihren Server festgelegt. Server-IDs sind in diesem Fall eine Liste von durch Kommas getrennten Serien-IDs, die über den Befehl !happen_allseries gefunden werden können. Das Festlegen von Favoritenserien ist erforderlich, um den Befehl !happen_currentseries zu verwenden.
    **!happen_currentseries** 
        - Sobald Lieblingsserien durch !happen_setfavseries wurden, druckt dieser Befehl Bilder, die die aktuellen Tracks für jede der Lieblingsserien für diese Rennwoche und die nächste Rennwoche zeigen.
    **!happen_addfavseries** 
        - Dies ist ähnlich wie !happen_setfavseries außer es fügt nur eine einzelne Serie zur Favoritenliste hinzu.
    **!happen_removefavseries** 
        - Dadurch wird ein einzelner Favorit aus der gespeicherten Favoritenserie entfernt.
    ''').strip().format(self.client.user)
    await self.print(commands_list_part_4)
    commands_list_part_5 = dedent('''
      -
      -
      **Leaderboard/Statistics**

      **!happen_recentraces <iRacing Client ID >** 
        - Dies gibt detaillierte Informationen über die letzten 10 Rennen des angegebenen Benutzers. Wenn keine iRacing Client-ID angegeben wird, wird standardmäßig die gespeicherte ID des Benutzers angegeben, der sie aufgerufen hat. Wenn der Benutzer, der sie aufgerufen hat, ihre ID nicht gespeichert hat, muss er beim Aufrufen eine ID angeben.
      **!happen_update** 
        - Dadurch werden die gespeicherten Informationen nur für den Benutzer aktualisiert, der den Befehl aufgerufen hat.
      **!happen_updateserver** 
        - Dadurch werden die gespeicherten Informationen für alle Benutzer in der Discord für die Verwendung des Befehls !happen_leaderboard aktualisiert. Alle Zwietracht werden automatisch stündlich aktualisiert, so dass dies oft nicht mehr möglich ist. **HINWEIS:** Die iRacing-API wird nicht häufig aktualisiert, also selbst wenn Sie ein Rennen vor kurzem beendet haben und Änderungen erwarten, kann es bis zu einem Tag dauern, bis diejenigen auf dem Bot durchkommen.
    ''').strip().format(self.client.user)
    await self.print(commands_list_part_5)
    commands_list_part_6 = dedent('''
          **!happen_leaderboard <category> <type>** 
        - Dadurch wird eine Bestenliste aller Benutzer mit gespeicherten IDs (über den Befehl !happen_saveid) für die angegebene Kategorie und den angegebenen Typ gedruckt. Kategorie kann jede von Straße, oval, Dirtroad und Dirtoval sein, aber es ist Standard auf Straße. Typ ist entweder Karriere oder jährlich, und es ist standard. karriere wird alle Zeitdaten anzeigen, und jährlich werden nur Daten aus dem laufenden Jahr angezeigt. **HINWEIS:** Dies kann mit einer Kategorie und keinem Typ aufgerufen werden, aber wenn Sie mit einem Typ anrufen möchten, müssen Sie eine Kategorie übergeben. Zum Beispiel kann ich !happen_leaderboard oval nennen, aber wenn ich die Straßenbestenliste jährlich angeben möchte, muss ich angeben: !happen_leaderboard Straße jährlich, !happen_leaderboard Jahr ist NICHT gültig.
      **!happen_careerstats <iRacing Client ID>** 
        - Dies gibt einen Überblick über die Karrierestatistiken des Spielers mit der angegebenen iRacing Client ID. Wenn keine iRacing Client-ID angegeben wird, wird die gespeicherte ID für den Benutzer verwendet, der den Befehl aufgerufen hat. Wenn der Benutzer seine ID nicht gespeichert hat, muss er eine iRacing-Client-ID angeben.
      **!happen_yearlystats <iRacing Client ID>** 
        - Dies gibt einen Überblick über die jährlichen Statistiken des Spielers mit der angegebenen iRacing Client ID. Wenn keine iRacing Client-ID angegeben wird, wird die gespeicherte ID für den Benutzer verwendet, der den Befehl aufgerufen hat. Wenn der Benutzer seine ID nicht gespeichert hat, muss er eine iRacing-Client-ID angeben.
        ''').strip().format(self.client.user)
    await self.print(commands_list_part_6)
  
  def parse_driver_identifier(self, text):
    identifier = text.strip()
    last_id_part = identifier.split(' ')[-1]
    if last_id_part.isnumeric():
      return int(last_id_part)
    return identifier
  
  def parse_driver_identifiers(self, command_text, command_prefix, collection=False):
    drivers_text = self.parse_target(command_text, command_prefix)
    if collection:
      return [[self.parse_driver_identifier(driver) for driver in team_text.split(DRIVER_SEPARATOR)] for team_text in drivers_text.split(TEAM_SEPARATOR)]
    else:
      return [self.parse_driver_identifier(driver) for driver in drivers_text.replace(TEAM_SEPARATOR, DRIVER_SEPARATOR).split(DRIVER_SEPARATOR)]
  
  def parse_integer_list(self, list_text):
    return [int(int_text.strip()) for int_text in list_text.split(DRIVER_SEPARATOR) if int_text.strip().isnumeric()]
  
  def parse_target(self, command_text, command_prefix):
    return command_text.split(command_prefix)[1].strip()
  
  async def perform_background_recheck(self, guild_id):
    self.bot.initialize_guild(guild_id)
    channel_id = self.bot.get_monitoring_data().get('channel_id')
    if not channel_id:
      return
    self.channel = self.client.get_channel(channel_id)
    if not self.channel:
      return
    self.bot.set_guild_name(self.channel.guild.name)
    await self.bot.background_recheck()
  
  async def print(self, message):
    if self.channel:
      await self.channel.send(message)
  
  async def process_request(self, message):
    self.message = message
    self.channel = message.channel
    self.bot.initialize_guild(message.channel.guild.id)
    self.bot.set_guild_name(message.channel.guild.name)
    cmd = self.strip_mention().strip()
    if cmd.startswith('list commands'):
      await self.list_commands()
    elif cmd.startswith('status'):
      await self.bot.show_status()
    elif cmd.startswith('drivers'):
      await self.bot.list_drivers()
    elif cmd.startswith('add driver'):
      await self.bot.add_drivers(self.parse_driver_identifiers(cmd, 'add driver'))
    elif cmd.startswith('remove driver'):
      await self.bot.remove_drivers(self.parse_driver_identifiers(cmd, 'remove driver'))
    elif cmd.startswith('clear drivers'):
      await self.bot.clear_drivers()
    elif cmd.startswith('recheck rating'):
      target = self.parse_target(cmd, 'recheck rating')
      if target == 'all':
        await self.bot.recheck_all_ratings()
      else:
        await self.bot.recheck_ratings(self.parse_driver_identifiers(cmd, 'recheck rating'))
    elif cmd.startswith('team sizes'):
      await self.bot.list_team_sizes()
    elif cmd.startswith('set team sizes'):
      team_sizes = self.parse_integer_list(self.parse_target(cmd, 'set team sizes'))
      await self.bot.set_team_sizes(team_sizes)
    elif cmd.startswith('combinations'):
      await self.bot.list_combinations()
    elif cmd.startswith('combine drivers'):
      await self.bot.add_combinations(self.parse_driver_identifiers(cmd, 'combine drivers', collection=True))
    elif cmd.startswith('remove combination'):
      await self.bot.remove_combinations(self.parse_driver_identifiers(cmd, 'remove combination', collection=True))
    elif cmd.startswith('clear combinations'):
      await self.bot.clear_combinations()
    elif cmd.startswith('balance threshold'):
      await self.bot.show_balance_threshold()
    elif cmd.startswith('set balance threshold'):
      await self.bot.set_balance_threshold(int(self.parse_target(cmd, 'set balance threshold')))
    elif cmd.startswith('balance'):
      await self.bot.list_balance()
    elif cmd.startswith('recalculate balance'):
      await self.bot.recalculate_balance()
    elif cmd.startswith('teams'):
      await self.bot.list_teams()
    elif cmd.startswith('set teams'):
      if self.parse_target(cmd, 'set teams') == 'according to balance':
        await self.bot.set_teams_according_to_balance()
      else:
        await self.bot.set_teams(self.parse_driver_identifiers(cmd, 'set teams', collection=True))
    elif cmd.startswith('clear teams'):
      await self.bot.clear_teams()
    elif cmd.startswith('notification channel'):
      channel_id = self.bot.get_monitoring_data().get('channel_id')
      if channel_id:  
        found_channel = discord.utils.find(lambda c: c.id == channel_id and c.type == discord.ChannelType.text, self.channel.guild.channels)
        if found_channel:
          await self.print('I am currently sending notifications to {0}.'.format(found_channel.mention))
        else:
          await self.print("Oops, the channel I am currently sending notifications to doesn't seem to exist anymore. If desired, please set a new channel.")
      else:
        await self.print('No channel is currently configured for notifications.')
    elif cmd.startswith('set notification channel'):
      monitoring_data = {'channel_id': self.channel.id}
      self.bot.set_monitoring_data(monitoring_data)
      await self.print('Set {0} as the notification channel.'.format(self.channel.mention))
    elif cmd.startswith('test background recheck'):
      await self.bot.background_recheck()
    else:
      await self.bot.alert_unrecognized_command()
  
  def set_bot(self, bot):
    self.bot = bot
  
  def strip_mention(self):
    re_match = MESSAGE_TEXT_RE.match(self.message.content)
    return re_match.group(1)