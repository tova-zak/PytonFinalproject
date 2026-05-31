
import click
import core as wit


@click.group()
def cli():
    pass


@cli.command()
def init():
    click.echo(wit.init_repo())


@cli.command()
@click.argument("path")
def add(path):
    click.echo(wit.add(path))


@cli.command()
@click.option("-m", "--message", required=True)
def commit(message):
    click.echo(wit.commit(message))


@cli.command()
def status():
    staged, untracked = wit.status()

    click.echo("\n--- Status ---")
    click.echo("Staged files:")
    for f in staged:
        click.echo(f"  {f}")

    click.echo("\nUntracked files:")
    for f in untracked:
        click.echo(f"  {f}")


@cli.command()
@click.argument("commit_id")
def checkout(commit_id):
    click.echo(wit.checkout(commit_id))


@cli.command()
def push():
    """שליחת קבצי ה-Commit האחרון לניתוח סטטי והפקת גרפים בשרת"""
    result = wit.push_commit_to_server()

    # בדיקה האם חזרה שגיאה מהפונקציה
    if "error" in result:
        click.secho(f"❌ Error: {result['error']}", fg="red", bold=True)
        return

    # הדפסת דוח הבדיקה בטרמינל
    click.secho("\n" + "=" * 45, fg="cyan", bold=True)
    click.secho("🛡️  CODEGUARD QUALITY ANALYSIS REPORT  🛡️", fg="cyan", bold=True)
    click.secho("=" * 45, fg="cyan", bold=True)

    # הדפסת האזהרות שהתקבלו מה-Analyzer
    if result.get("alerts"):
        for file_name, file_alerts in result["alerts"].items():
            click.secho(f"\n📄 File: {file_name}", fg="yellow", underline=True, bold=True)
            for alert in file_alerts:
                click.echo(f"  ⚠️  {alert}")
    else:
        click.secho("\n✅ Excellent! No quality issues found in your code.", fg="green", bold=True)

    #  הדפסת הקישורים הישירים לצפייה בגרפים הסטטיסטיים
    click.secho("\n📊 Generated Visual Analytics:", fg="magenta", bold=True)
    for link in result.get("graphs", []):
        click.echo(f"  🔗 {link}")

    click.secho("=" * 45 + "\n", fg="cyan", bold=True)

if __name__ == "__main__":
    cli()


