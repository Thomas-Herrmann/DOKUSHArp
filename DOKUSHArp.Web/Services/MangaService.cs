using System.Security.Cryptography;
using System.Text.Json;

namespace DOKUSHArp.Web.Services;

public sealed class MangaService(HttpClient client)
{
	private static readonly JsonSerializerOptions SerializationOptions = MakeSerializationOptions();

	public async Task<IReadOnlyList<MangaMetaRecord>> GetMangasAsync(CancellationToken cancellationToken = default) => await client
		.GetFromJsonAsAsyncEnumerable<MangaMetaRecord>("/mangas", SerializationOptions, cancellationToken)
		.OfType<MangaMetaRecord>()
		.ToListAsync(cancellationToken: cancellationToken)
		.ConfigureAwait(false);

	public async Task<MangaPage> GetMangaPageAsync(string mangaId, int pageIndex, CancellationToken cancellationToken = default) => await client
		.GetFromJsonAsync<MangaPage>($"/manga/{mangaId}/page/{pageIndex}", SerializationOptions, cancellationToken)
		.ConfigureAwait(false) ?? throw new InvalidOperationException("Unable to fetch page");

	public async Task UploadManga(Stream epubFileStream, string title, int coverPageCount, CancellationToken cancellationToken = default)
	{
		using var md5Handle = MD5.Create();
		var fileHash = md5Handle.ComputeHash(epubFileStream);

		epubFileStream.Position = 0;

		var id = Guid.NewGuid();

		await BeginUpload(fileHash, title, coverPageCount, id, cancellationToken).ConfigureAwait(false);

		var buffer = new byte[16384];
		int countRead;

		while ((countRead = await epubFileStream.ReadAsync(buffer, cancellationToken).ConfigureAwait(false)) > 0)
			await UploadChunk(buffer, countRead, id, cancellationToken).ConfigureAwait(false);

		await EndUpload(id, cancellationToken).ConfigureAwait(false);
	}

	private static JsonSerializerOptions MakeSerializationOptions()
	{
		var options = new JsonSerializerOptions { PropertyNameCaseInsensitive = true };

		options.Converters.Add(new BoundingBoxConverter());

		return options;
	}

	private async Task BeginUpload(byte[] fileHash, string title, int coverPageCount, Guid id, CancellationToken cancellationToken)
	{
		using var hashContent = new ByteArrayContent(fileHash);

		hashContent.Headers.Add("Content-Type", "application/epub+zip");

		using var response = await client
			.PostAsync($"/upload_begin?title={title}&coverPageCount={coverPageCount}&id={id}", hashContent, cancellationToken)
			.ConfigureAwait(false);

		response.EnsureSuccessStatusCode();
	}

	private async Task UploadChunk(byte[] chunk, int count, Guid id, CancellationToken cancellationToken)
	{
		using var chunkContent = new ByteArrayContent(chunk, 0, count);
		using var chunkResponse = await client
			.PostAsync($"/upload_chunk?id={id}", chunkContent, cancellationToken)
			.ConfigureAwait(false);

		chunkResponse.EnsureSuccessStatusCode();
	}

	private async Task EndUpload(Guid id, CancellationToken cancellationToken)
	{
		using var response = await client
			.PostAsync($"/upload_end?id={id}", null, cancellationToken)
			.ConfigureAwait(false);

		response.EnsureSuccessStatusCode();
	}
}
