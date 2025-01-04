namespace DOKUSHArp.Web.Services;

public sealed record MangaPage
{
	public required IReadOnlyList<BoundingBox> BoundingBoxes { get; set; }

	public required string TranslatedImage { get; set; }

	public required string OriginalImage { get; set; }
}
