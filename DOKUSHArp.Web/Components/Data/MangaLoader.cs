using DOKUSHArp.Web.Components.Store;
using DOKUSHArp.Web.Components.Store.Manga;
using DOKUSHArp.Web.Services;
using Microsoft.AspNetCore.Components;
using System.Collections.Immutable;

namespace DOKUSHArp.Web.Components.Data;

public sealed class MangaLoader : LoaderComponent
{
	[Inject] private State<MangaState> State { get; set; } = default!;

	[Inject] private MangaService MangaService { get; set; } = default!;

	protected override async Task LoadAsync()
	{
		if (State.Value.HasInitialized) return;

		Load:
		try
		{
			var mangaRecords = await MangaService.GetMangasAsync().ConfigureAwait(false);

			await State.UpdateAsync(state => state with
			{
				AvailableManga = ImmutableDictionary
				.CreateRange(StringComparer.OrdinalIgnoreCase, mangaRecords
				.Select(record => new KeyValuePair<string, MangaReaderMeta>(record.Id, new MangaReaderMeta { Title = record.Title, NumCoverPages = record.NumCoverPages }))),
				IsLoading = false,
				HasInitialized = true
			}).ConfigureAwait(false);
		}
		catch
		{
			await Task.Delay(500);

			goto Load;
		}
	}
}