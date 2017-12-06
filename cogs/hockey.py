import discord
import aiohttp
import asyncio
import json
import os
from datetime import datetime
from discord.ext import commands
from .utils.dataIO import dataIO
from .utils import checks
try:
    from .oilers import Oilers
except ImportError:
    pass

numbs = {
    "next": "➡",
    "back": "⬅",
    "exit": "❌"
}
class Hockey:

    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)
        self.settings = dataIO.load_json("data/hockey/settings.json")
        self.url = "https://statsapi.web.nhl.com"
        self.teams = dataIO.load_json("data/hockey/teams.json")
        self.headshots = "https://nhl.bamcontent.com/images/headshots/current/168x168/{}.jpg"
        self.loop = bot.loop.create_task(self.check_team_goals())

    def __unload(self):
        self.loop.cancel()

    @commands.command(pass_context=True)
    async def testgoallights(self, ctx):
        hue = Oilers(self.bot)
        await hue.oilersgoal2()

    async def team_playing(self, games):
        """Check if team is playing and returns game link and team name"""
        is_playing = False
        links = {}
        for game in games:
            if game["teams"]["away"]["team"]["name"] in self.settings and game["status"]["abstractGameState"] != "Final":
                is_playing = True
                links[game["teams"]["away"]["team"]["name"]] = game["link"]
            if game["teams"]["home"]["team"]["name"] in self.settings and game["status"]["abstractGameState"] != "Final":
                is_playing =True
                links[game["teams"]["home"]["team"]["name"]] = game["link"]
        return is_playing, links

    async def check_team_goals(self):
        """Loop to check what teams are playing and see if a goal was scored"""
        await self.bot.wait_until_ready()
        while self is self.bot.get_cog("Hockey"):
            async with self.session.get(self.url + "/api/v1/schedule") as resp:
                data = await resp.json()
            is_playing, games = await self.team_playing(data["dates"][0]["games"])
            num_goals = 0
            print(games)
            while is_playing and games != {}:
                for team, link in games.items():
                    # print(team)
                    async with self.session.get(self.url + link) as resp:
                        data = await resp.json()
                    # print(data)
                    event = data["liveData"]["plays"]["allPlays"]
                    home_team = data["liveData"]["linescore"]["teams"]["home"]["team"]["name"]
                    home_shots = data["liveData"]["linescore"]["teams"]["home"]["shotsOnGoal"]
                    home_score = data["liveData"]["linescore"]["teams"]["home"]["goals"]
                    away_team = data["liveData"]["linescore"]["teams"]["away"]["team"]["name"]
                    away_shots = data["liveData"]["linescore"]["teams"]["away"]["shotsOnGoal"]
                    away_score = data["liveData"]["linescore"]["teams"]["away"]["goals"]
                    score_msg = {"Home":home_team, "Home Score":home_score, "Home Shots":home_shots,
                                 "Away": away_team, "Away Score":away_score, "Away Shots":away_shots}
                    goals = [goal for goal in event if goal["result"]["eventTypeId"] == "GOAL" and goal["team"]["name"] == team]
                    if len(goals) == 0:
                        continue
                    for goal in goals:
                        if goal["about"]["eventId"] not in self.settings[team]["goal_id"]:
                            msg = await self.post_team_goal(goal, team, score_msg)
                            self.settings[team]["goal_id"].append(goal["about"]["eventId"])
                            dataIO.save_json("data/hockey/settings.json", self.settings)
                if data["gameData"]["status"]["abstractGameState"] == "Final":
                    # print("Final")
                    self.settings[team]["goal_id"] = []
                    dataIO.save_json("data/hockey/settings.json", self.settings)
                    del games[team]
                if games == {}:
                    is_playing = False
                    break
                await asyncio.sleep(60)
            print(is_playing)
            await asyncio.sleep(300)

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def hockeytwitter(self, ctx):
        server = self.bot.get_server(id="381567805495181344")
        for team in self.teams:
            team = team.replace(".", "")
            team = team.replace(" ", "-")
            if team.startswith("Montr"):
                team = "montreal-canadiens"
            await self.bot.create_channel(server, name=team.lower() + "-twitter")

    async def post_team_goal(self, goal, team, score_msg):
        """Creates embed and sends message if a team has scored a goal"""
        em = discord.Embed(description=goal["result"]["description"],
                           colour=int(self.teams[goal["team"]["name"]]["home"].replace("#", ""), 16))
        scorer = self.headshots.format(goal["players"][0]["player"]["id"])
        scoring_team = self.teams[goal["team"]["name"]]
        period = goal["about"]["ordinalNum"]
        period_time_left = goal["about"]["periodTimeRemaining"]
        em.set_author(name="🚨 " + goal["team"]["name"] + " GOAL 🚨", 
                      url=self.teams[goal["team"]["name"]]["team_url"],
                      icon_url=self.teams[goal["team"]["name"]]["logo"])
        em.add_field(name=score_msg["Home"], value=score_msg["Home Score"])
        em.add_field(name=score_msg["Away"], value=score_msg["Away Score"])
        em.add_field(name="Shots " + score_msg["Home"], value=score_msg["Home Shots"])
        em.add_field(name="Shots " + score_msg["Away"], value=score_msg["Away Shots"])
        em.set_thumbnail(url=scorer)
        em.set_footer(text="{} left in the {} period".format(period_time_left, period))
        em.timestamp = datetime.strptime(goal["about"]["dateTime"], "%Y-%m-%dT%H:%M:%SZ")
        if "oilers" in goal["team"]["name"].lower():
            try:
                hue = Oilers(self.bot)
                await hue.oilersgoal2()
            except:
                pass
        role = None
        for channels in self.settings[team]["channel"]:
            server = self.bot.get_server(id="381567805495181344")
            for roles in server.roles:
                # role_name = roles.name + " GOAL"
                if roles.name == team + " GOAL":
                    role = roles
            channel = self.bot.get_channel(id=channels)
            if role is not None:
                return await self.bot.send_message(channel, role.mention, embed=em)
            else:  
                return await self.bot.send_message(channel, embed=em)

    @commands.group(pass_context=True, name="hockey", aliases=["nhl"])
    async def hockey_commands(self, ctx):
        """Various Hockey related commands"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @hockey_commands.command(hidden=True, pass_context=True)
    @checks.admin_or_permissions(manage_channels=True)
    async def add_goals(self, ctx, team, channel:discord.Channel=None):
        """Adds a hockey team goal updates to a channel"""
        try:
            team = [team_name for team_name in self.teams if team.lower() in team_name.lower()][0]
        except IndexError:
            await self.bot.say("{} is not an available team!".format(team))
            return
        if channel is None:
            channel = ctx.message.channel
        if team not in self.settings:
            self.settings[team] = {"channel":[channel.id], "goals":[], "goals_id": []}
        self.settings[team]["channel"].append(channel.id)
        dataIO.save_json("data/hockey/settings.json", self.settings)
        await self.bot.say("{} goals will be posted in {}".format(team, channel.mention))

    @hockey_commands.command(hidden=True, pass_context=True, name="del", aliases=["remove", "rem"])
    @checks.admin_or_permissions(manage_channels=True)
    async def remove_goals(self, ctx, team, channel:discord.Channel=None):
        """Removes a teams goal updates from a channel"""
        try:
            team = [team_name for team_name in self.teams if team.lower() in team_name.lower()][0]
        except IndexError:
            await self.bot.say("{} is not an available team!".format(team))
            return
        if channel is None:
            channel = ctx.message.channel
        if team not in self.settings:
            await self.bot.send_message(ctx.message.channel, "I am not posting {} goals in {}".format(team, channel.mention))
            return
        self.settings[team]["channel"].remove(channel.id)
        if self.settings[team]["channel"] == []:
            del self.settings[team]
        dataIO.save_json("data/hockey/settings.json", self.settings)
        await self.bot.say("{} goals will stop being posted in {}".format(team, channel.mention))

    @hockey_commands.command(pass_context=True, name="role")
    async def team_role(self, ctx, *, team):
        """Set your role to a team role"""
        server = ctx.message.server
        try:
            team = [team_name for team_name in self.teams if team.lower() in team_name.lower()][0]
        except IndexError:
            await self.bot.say("{} is not an available team!".format(team))
            return
        role = [role for role in server.roles if role.name == team][0]
        await self.bot.add_roles(ctx.message.author, role)
        await self.bot.send_message(ctx.message.channel, "Role applied.")

    @hockey_commands.command(pass_context=True, name="goals")
    async def team_goals(self, ctx, *, team=None):
        """Set your role to a team role"""
        server = ctx.message.server
        member = ctx.message.author
        if team is None:
            team = [role.name for role in member.roles if role.name in self.teams]
            for t in team:
                role = [role for role in server.roles if role.name == t + " GOAL"]
                for roles in role:
                    await self.bot.add_roles(ctx.message.author, roles)
                await self.bot.send_message(ctx.message.channel, "Role applied.")
        else:
            try:
                team = [team_name for team_name in self.teams if team.lower() in team_name.lower()][0]
            except IndexError:
                await self.bot.say("{} is not an available team!".format(team))
                return
            role = [role for role in server.roles if role.name == team][0]
            await self.bot.add_roles(ctx.message.author, role)
            await self.bot.send_message(ctx.message.channel, "Role applied.")

    async def game_menu(self, ctx, post_list: list,
                         team_set=None,
                         message: discord.Message=None,
                         page=0, timeout: int=30):
        """menu control logic for this taken from
           https://github.com/Lunar-Dust/Dusty-Cogs/blob/master/menu/menu.py"""

        game = post_list[page]
        async with self.session.get(self.url + game["link"]) as resp:
            game_data = await resp.json()
        home_team = game_data["liveData"]["linescore"]["teams"]["home"]["team"]["name"]
        home_shots = game_data["liveData"]["linescore"]["teams"]["home"]["shotsOnGoal"]
        home_score = game_data["liveData"]["linescore"]["teams"]["home"]["goals"]
        away_team = game_data["liveData"]["linescore"]["teams"]["away"]["team"]["name"]
        away_shots = game_data["liveData"]["linescore"]["teams"]["away"]["shotsOnGoal"]
        away_score = game_data["liveData"]["linescore"]["teams"]["away"]["goals"]
        logo = self.teams[home_team]["logo"] if team_set is None else self.teams[team_set]["logo"]
        team_url = self.teams[home_team]["team_url"] if team_set is None else self.teams[team_set]["team_url"]
        game_time = game["gameDate"]
        timestamp = datetime.strptime(game_time, "%Y-%m-%dT%H:%M:%SZ")
        game_state = game_data["gameData"]["status"]["abstractGameState"]
        title = "{away} @ {home} {state}".format(away=away_team, home=home_team, state=game_state)
        if team_set is None:
            colour = int(self.teams[home_team]["home"].replace("#", ""), 16)
        else:
            colour = int(self.teams[team_set]["home"].replace("#", ""), 16)
        em = discord.Embed(timestamp=timestamp, colour=colour)
        em.set_author(name=title, url=team_url, icon_url=logo)
        em.set_thumbnail(url=logo)
        em.add_field(name="Home Team", value=home_team)
        em.add_field(name="Away Team", value=away_team)
        if game_state != "Preview":
            em.add_field(name="Home Shots on Goal", value=home_shots)
            em.add_field(name="Away Shots on Goal", value=away_shots)
            em.add_field(name="Home Score", value=str(home_score))
            em.add_field(name="Away Score", value=str(away_score))
            if game_state == "Live":
                event = game_data["liveData"]["plays"]["allPlays"]
                period = game_data["liveData"]["linescore"]["currentPeriodOrdinal"]
                period_time_left = game_data["liveData"]["linescore"]["currentPeriodTimeRemaining"]
                goals = [goal for goal in event if goal["result"]["eventTypeId"] == "GOAL"]
                if period_time_left[0].isdigit():
                    msg = "{} Left in the {} period".format(period_time_left, period)
                else:
                    msg = "{} of the {} period".format(period_time_left, period)
                em.description = event[-1]["result"]["description"]
                if goals != []:
                    em.add_field(name="{} Goal".format(goals[-1]["team"]["name"]), value=goals[-1]["result"]["description"])
                em.add_field(name="Period", value=msg)
        em.set_footer(text="Game start ")
        if not message:
            message =\
                await self.bot.send_message(ctx.message.channel, embed=em)
            await self.bot.add_reaction(message, "⬅")
            await self.bot.add_reaction(message, "❌")
            await self.bot.add_reaction(message, "➡")
        else:
            message = await self.bot.edit_message(message, embed=em)
        react = await self.bot.wait_for_reaction(
            message=message, user=ctx.message.author, timeout=timeout,
            emoji=["➡", "⬅", "❌"]
        )
        if react is None:
            await self.bot.remove_reaction(message, "⬅", self.bot.user)
            await self.bot.remove_reaction(message, "❌", self.bot.user)
            await self.bot.remove_reaction(message, "➡", self.bot.user)
            return None
        reacts = {v: k for k, v in numbs.items()}
        react = reacts[react.reaction.emoji]
        if react == "next":
            next_page = 0
            if page == len(post_list) - 1:
                next_page = 0  # Loop around to the first item
            else:
                next_page = page + 1
            return await self.game_menu(ctx, post_list, team_set=team_set,
                                        message=message,
                                        page=next_page, timeout=timeout)
        elif react == "back":
            next_page = 0
            if page == 0:
                next_page = len(post_list) - 1  # Loop around to the last item
            else:
                next_page = page - 1
            return await self.game_menu(ctx, post_list, team_set=team_set,
                                        message=message,
                                        page=next_page, timeout=timeout)
        else:
            return await\
                self.bot.delete_message(message)

    async def roster_menu(self, ctx, post_list: list,
                         team_set,
                         message: discord.Message=None,
                         page=0, timeout: int=30):
        """menu control logic for this taken from
           https://github.com/Lunar-Dust/Dusty-Cogs/blob/master/menu/menu.py"""
        player_list = post_list[page]
        async with self.session.get(self.url + player_list["person"]["link"] + "?expand=person.stats&stats=yearByYear") as resp:
            player_data = await resp.json()
        player = player_data["people"][0]
        year_stats = [league for league in player["stats"][0]["splits"] if league["league"]["name"] == "National Hockey League"][-1]
        name = player["fullName"]
        number = player["primaryNumber"]
        position = player["primaryPosition"]["name"]
        headshot = self.headshots.format(player["id"])
        em = discord.Embed(colour=int(self.teams[team_set]["home"].replace("#", ""), 16))
        em.set_author(name="{} #{}".format(name, number), url=self.teams[team_set]["team_url"], icon_url=self.teams[team_set]["logo"])
        em.add_field(name="Position", value=position)
        em.set_thumbnail(url=headshot)
        if position != "Goalie":
            post_data = {"Shots" : year_stats["stat"]["shots"],
                        "Goals" : year_stats["stat"]["goals"],
                        "Assists" : year_stats["stat"]["assists"],
                        "Hits" : year_stats["stat"]["hits"],
                        "Face Off Percent" : year_stats["stat"]["faceOffPct"],
                        "+/-" : year_stats["stat"]["plusMinus"],
                        "Blocked Shots" : year_stats["stat"]["blocked"],
                        "PIM" : year_stats["stat"]["pim"]}
            for key, value in post_data.items():
                if value != 0.0:
                    em.add_field(name=key, value=value)
        else:
            saves = year_stats["stat"]["saves"]
            save_percentage = year_stats["stat"]["savePercentage"]
            goals_against_average = year_stats["stat"]["goalAgainstAverage"]
            em.add_field(name="Saves", value=saves)
            em.add_field(name="Save Percentage", value=save_percentage)
            em.add_field(name="Goals Against Average", value=goals_against_average)
        
        if not message:
            message =\
                await self.bot.send_message(ctx.message.channel, embed=em)
            await self.bot.add_reaction(message, "⬅")
            await self.bot.add_reaction(message, "❌")
            await self.bot.add_reaction(message, "➡")
        else:
            message = await self.bot.edit_message(message, embed=em)
        react = await self.bot.wait_for_reaction(
            message=message, user=ctx.message.author, timeout=timeout,
            emoji=["➡", "⬅", "❌"]
        )
        if react is None:
            await self.bot.remove_reaction(message, "⬅", self.bot.user)
            await self.bot.remove_reaction(message, "❌", self.bot.user)
            await self.bot.remove_reaction(message, "➡", self.bot.user)
            return None
        reacts = {v: k for k, v in numbs.items()}
        react = reacts[react.reaction.emoji]
        if react == "next":
            next_page = 0
            if page == len(post_list) - 1:
                next_page = 0  # Loop around to the first item
            else:
                next_page = page + 1
            return await self.roster_menu(ctx, post_list, team_set=team_set,
                                        message=message,
                                        page=next_page, timeout=timeout)
        elif react == "back":
            next_page = 0
            if page == 0:
                next_page = len(post_list) - 1  # Loop around to the last item
            else:
                next_page = page - 1
            return await self.roster_menu(ctx, post_list, team_set=team_set,
                                        message=message,
                                        page=next_page, timeout=timeout)
        else:
            return await\
                self.bot.delete_message(message)


    @hockey_commands.command(pass_context=True)
    async def games(self, ctx, *, team=None):
        """Gets all NHL games this season or selected team"""
        games_list = []
        page_num = 0
        today = datetime.today()
        url = "{base}/api/v1/schedule?startDate={year}-9-1&endDate={year2}-9-1"\
              .format(base=self.url, year=today.year, year2=today.year+1)
        
        if team is not None:
            try:
                team = [team_name for team_name in self.teams if team.lower() in team_name.lower()][0]
            except IndexError:
                await self.bot.send_message(ctx.message.channel, "{} Does not appear to be an NHL team!".format(team))
                return
            url += "&teamId={}".format(self.teams[team]["id"])
        async with self.session.get(url) as resp:
            data = await resp.json()
        for dates in data["dates"]:
            games_list += [game for game in dates["games"]]
        for game in games_list:
            game_time = datetime.strptime(game["gameDate"], "%Y-%m-%dT%H:%M:%SZ")
            if game_time >= today:
                page_num = games_list.index(game)
                break
        if games_list != []:
            await self.game_menu(ctx, games_list, team, None, page_num)
        else:
            await self.bot.send_message(ctx.message.channel, "{} have no recent or upcoming games!".format(team))

    @hockey_commands.command(pass_context=True)
    async def players(self, ctx, *, team):
        """Gets the current team roster"""
        try:
            team = [team_name for team_name in self.teams if team.lower() in team_name.lower()][0]
        except IndexError:
            await self.bot.send_message(ctx.message.channel, "{} Does not appear to be an NHL team!".format(team))
            return
        url = "{}/api/v1/teams/{}/roster".format(self.url, self.teams[team]["id"])
        print(url)
        async with self.session.get(url) as resp:
            data = await resp.json()

        await self.roster_menu(ctx, data["roster"], team)

def check_folder():
    if not os.path.exists("data/hockey"):
        print("Creating data/tweets folder")
        os.makedirs("data/hockey")

def check_file():
    data = {}
    f = "data/hockey/settings.json"
    if not dataIO.is_valid_json(f):
        print("Creating default settings.json...")
        dataIO.save_json(f, data)

def setup(bot):
    check_folder()
    check_file()
    bot.add_cog(Hockey(bot))