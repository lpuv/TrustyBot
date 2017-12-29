from discord.ext import commands
import discord
from cogs.utils import checks
import asyncio
import os
from datetime import datetime

try:
    import psutil
except Exception as e:
    raise RuntimeError("You must run `pip3 install psutil` to use this cog") from e


class SysInfo:
    """Display CPU, Memory, Disk and Network information"""

    options = ('cpu', 'memory', 'file', 'disk', 'network', 'boot')

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, name='sysinfo')
    @checks.is_owner()
    async def psutil(self, ctx, *args: str):
        """Show CPU, Memory, Disk, and Network information

         Usage: sysinfo [option]

         Examples:
             sysinfo           Shows all available info
             sysinfo cpu       Shows CPU usage
             sysinfo memory    Shows memory usage
             sysinfo file      Shows full path of open files
             sysinfo disk      Shows disk usage
             sysinfo network   Shows network usage
             sysinfo boot      Shows boot time
         """
        em = discord.Embed()
        # CPU
        cpu_count_p = psutil.cpu_count(logical=False)
        cpu_count_l = psutil.cpu_count()
        if cpu_count_p is None:
            cpu_count_p = "N/A"

        cpu_cs = ("{0:<9}: {1:>3}".format("Physical", cpu_count_p) +
                  "\n{0:<9}: {1:>3}".format("Logical", cpu_count_l))
        em.add_field(name="CPU Count 💻", value= cpu_cs)
        psutil.cpu_percent(interval=None, percpu=True)
        await asyncio.sleep(1)
        cpu_p = psutil.cpu_percent(interval=None, percpu=True)
        cpu_ps = ("{0:<8}: {1}".format("Per CPU", cpu_p) +
                  "\n{0:<8}: {1:.1f}%".format("Overall", sum(cpu_p)/len(cpu_p)))
        em.add_field(name="CPU usage 📈", value= cpu_ps)
        cpu_t = psutil.cpu_times()
        width = max([len("{:,}".format(int(n))) for n in [cpu_t.user, cpu_t.system, cpu_t.idle]])
        cpu_ts = ("CPU Times"
                  "{0:<7}: {1:>{width},}".format("User", int(cpu_t.user), width=width) +
                  "\n{0:<7}: {1:>{width},}".format("System", int(cpu_t.system), width=width) +
                  "\n{0:<7}: {1:>{width},}".format("Idle", int(cpu_t.idle), width=width))
        em.add_field(name="CPU times ⏱", value= cpu_ts, inline=True)

        # Memory
        mem_v = psutil.virtual_memory()
        width = max([len(self._size(n)) for n in [mem_v.total, mem_v.available, (mem_v.total - mem_v.available)]])
        mem_vs = ("{0:<10}: {1:>{width}}".format("Total", self._size(mem_v.total), width=width) +
                  "\n{0:<10}: {1:>{width}}".format("Available", self._size(mem_v.available), width=width) +
                  "\n{0:<10}: {1:>{width}} {2}%".format("Used", self._size(mem_v.total - mem_v.available),
                                                          mem_v.percent, width=width))
        em.add_field(name="Virtual Memory", value=mem_vs, inline=True)
        mem_s = psutil.swap_memory()
        width = max([len(self._size(n)) for n in [mem_s.total, mem_s.free, (mem_s.total - mem_s.free)]])
        mem_ss = ("{0:<6}: {1:>{width}}".format("Total", self._size(mem_s.total), width=width) +
                  "\n{0:<6}: {1:>{width}}".format("Free", self._size(mem_s.free), width=width) +
                  "\n{0:<6}: {1:>{width}} {2}%".format("Used", self._size(mem_s.total - mem_s.free),
                                                         mem_s.percent, width=width))
        em.add_field(name="Swap Memory", value=mem_ss, inline=True)

        # Open files
        open_f = psutil.Process().open_files()
        open_fs = ""
        if open_f:
            if hasattr(open_f[0], "mode"):
                open_fs += "".join(["{0} [{1}]".format(f.path, f.mode) for f in open_f])
            else:
                open_fs += "\n".join(["{0}".format(f.path) for f in open_f])
        else:
            open_fs += "None"
        em.add_field(name="Open File Handles", value=open_fs, inline=True)

        # Disk usage
        disk_u = psutil.disk_usage(os.path.sep)
        width = max([len(self._size(n)) for n in [disk_u.total, disk_u.free, disk_u.used]])
        disk_us = ("{0:<6}: {1:>{width}}".format("Total", self._size(disk_u.total), width=width) +
                   "\n{0:<6}: {1:>{width}}".format("Free", self._size(disk_u.free), width=width) +
                   "\n{0:<6}: {1:>{width}} {2}%".format("Used", self._size(disk_u.used),
                                                          disk_u.percent, width=width))
        em.add_field(name="Disk Usage", value=disk_us, inline=True)

        # Network
        net_io = psutil.net_io_counters()
        width = max([len(self._size(n)) for n in [net_io.bytes_sent, net_io.bytes_recv]])
        net_ios = ("{0:<11}: {1:>{width}}".format("Bytes sent", self._size(net_io.bytes_sent), width=width) +
                   "\n{0:<11}: {1:>{width}}".format("Bytes recv", self._size(net_io.bytes_recv), width=width))
        em.add_field(name="Network", value=net_ios, inline=True)

        # Boot time
        boot_s = datetime.fromtimestamp(psutil.boot_time())
        em.timestamp = boot_s
        em.set_footer(text="Boot Time")

        # Output
        await self.bot.send_message(ctx.message.channel, embed=em)

        return

    def _size(self, num):
        for unit in ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB", "ZB"]:
            if abs(num) < 1024.0:
                return "{0:.1f}{1}".format(num, unit)
            num /= 1024.0
        return "{0:.1f}{1}".format(num, "YB")


def setup(bot):
    n = SysInfo(bot)
    bot.add_cog(n)
