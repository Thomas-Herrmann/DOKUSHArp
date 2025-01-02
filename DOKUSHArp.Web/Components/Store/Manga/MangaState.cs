using DOKUSHArp.Web.Services;
using System.Collections.Immutable;

namespace DOKUSHArp.Web.Components.Store.Manga;

public sealed record MangaState : IState<MangaState>
{
	public static MangaState Default => new();

	public IImmutableDictionary<string, MangaReaderMeta> AvailableManga { get; set; } = ImmutableDictionary<string, MangaReaderMeta>.Empty;

	public bool HasInitialized { get; set; }

	public bool IsLoading { get; set; } = true;
}
